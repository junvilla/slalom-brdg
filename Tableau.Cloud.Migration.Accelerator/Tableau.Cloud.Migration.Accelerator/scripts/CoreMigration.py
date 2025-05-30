# Copyright (c) 2023, Salesforce, Inc.
# SPDX-License-Identifier: Apache-2
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This application is meant to use the migration modules directly from source.
# It builds the dotnet binaries and puts them on the path.

# Class python imports
import configparser
import logging
import os
import sys
import time as t
import datetime
import tableau_migration
from threading import Thread
from dotenv import load_dotenv  # Used to load environment variables (e.g., PAT secrets)
from logging_config import *

# tableau_migration and migration_testcomponents
from tableau_migration import (
    MigrationManifestSerializer,
    MigrationManifest,
    IMigrationManifestEntry,
    MigrationManifestEntryStatus,
)

from tableau_migration.migration import PyMigrationResult
from migration_hooks import *
from migration_filters import *
from migration_mappings import *
from migration_transformers import *

# CSharp Import
from Tableau.Migration.Engine.Pipelines import ServerToCloudMigrationPipeline

config = configparser.ConfigParser()
config.read("config.ini")

# Setup and initialize logging
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

# Get the absolute path of the current file
# and set the working directory
script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
os.chdir(script_directory)

# Check if directories exist; if not, create them.
if not os.path.exists(config["LOG"]["FOLDER_PATH"]):
    os.mkdir(config["LOG"]["FOLDER_PATH"])

if not os.path.exists(config["LOG"]["MANIFEST_FOLDER_PATH"]):
    os.mkdir(config["LOG"]["MANIFEST_FOLDER_PATH"])

serializer = MigrationManifestSerializer()


class Program:
    """Main program class."""

    done = False
    now_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def __init__(self):
        """Program init, sets up logging."""
        # Send all log messages to file
        filename_template = (
            config["LOG"]["FOLDER_PATH"] + "Tableau.Migration-" + self.now_str + ".log"
        )
        logging.basicConfig(
            filename=filename_template,
            format="%(asctime)s|%(levelname)s|%(name)s|%(message)s",
            level=logging.INFO,
        )

        # Create main migration app logger
        self.logger = logging.getLogger("Tableau.Migration")
        self.logger.setLevel(logging.DEBUG)

        # main migration app logger should write to console as well
        self.consoleHandler = logging.StreamHandler(sys.stdout)
        self.consoleHandler.setFormatter(
            logging.Formatter(
                "[%(asctime)s %(levelname).3s] %(message)s", datefmt="%H:%M:%S"
            )
        )
        self.logger.addHandler(self.consoleHandler)

    def load_manifest(self, manifest_path: str) -> MigrationManifest | None:
        """Loads a manifest if requested."""
        manifest = serializer.load(manifest_path)

        if manifest is not None:
            while True:
                answer = input(
                    f"Existing Manifest found at {manifest_path}. Should it be used? [Y/n] "
                ).upper()

                if answer == "N":
                    return None
                elif answer == "Y" or answer == "":
                    return manifest

        return None

    def print_result(self, result: PyMigrationResult):
        """Prints the result of a migration."""
        self.logger.info(f"Result: {result.status}")

        for pipeline_content_type in ServerToCloudMigrationPipeline.ContentTypes:
            content_type = pipeline_content_type.ContentType

            result.manifest.entries
            type_entries = [
                IMigrationManifestEntry(x)
                for x in result.manifest.entries.ForContentType(content_type)
            ]

            count_total = len(type_entries)

            count_migrated = 0
            count_skipped = 0
            count_errored = 0
            count_cancelled = 0
            count_pending = 0

            for entry in type_entries:
                if entry.status == MigrationManifestEntryStatus.MIGRATED:
                    count_migrated += 1
                elif entry.status == MigrationManifestEntryStatus.SKIPPED:
                    count_skipped += 1
                elif entry.status == MigrationManifestEntryStatus.ERROR:
                    count_errored += 1
                elif entry.status == MigrationManifestEntryStatus.CANCELED:
                    count_cancelled += 1
                elif entry.status == MigrationManifestEntryStatus.PENDING:
                    count_pending += 1

            output = f"""
            {content_type.Name}
            \t{count_migrated}/{count_total} succeeded
            \t{count_skipped}/{count_total} skipped
            \t{count_errored}/{count_total} errored
            \t{count_cancelled}/{count_total} cancelled
            \t{count_pending}/{count_total} pending
            """

            self.logger.info(output)

    def migrate(self):
        """The main migration function."""
        self.logger.info("Starting migration")

        # Load the environment variables
        load_dotenv()

        # Set the manifest path
        current_file_path = os.path.abspath(__file__)
        manifest_path = os.path.join(
            os.path.dirname(current_file_path), "MANIFEST", "manifest.json"
        )

        # Setup base objects for migrations
        plan_builder = tableau_migration.MigrationPlanBuilder()
        migration = tableau_migration.Migrator()

        # Build the plan
        plan_builder = (
            plan_builder.from_source_tableau_server(
                server_url=config["SOURCE"]["URL"],
                site_content_url=config["SOURCE"]["SITE_CONTENT_URL"],
                access_token_name=config["SOURCE"]["ACCESS_TOKEN_NAME"],
                access_token=os.environ.get("SOURCE_TOKEN_SECRET"),
            )
            .to_destination_tableau_cloud(
                pod_url=config["DESTINATION"]["URL"],
                site_content_url=config["DESTINATION"]["SITE_CONTENT_URL"],
                access_token_name=config["DESTINATION"]["ACCESS_TOKEN_NAME"],
                access_token=os.environ.get("DESTINATION_TOKEN_SECRET"),
            )
            .for_server_to_cloud()
            .with_tableau_id_authentication_type()
            .with_tableau_cloud_usernames(config["USERS"]["EMAIL_DOMAIN"])
        )

        ### Add hooks here.
        self.logger.info("Adding Hooks...")
        TimeLoggerAfterActionHook.handler = self.consoleHandler
        plan_builder.hooks.add(TimeLoggerAfterActionHook)
        plan_builder.hooks.add(SaveUserManifestHook)
        plan_builder.hooks.add(SaveGroupManifestHook)
        plan_builder.hooks.add(SaveProjectManifestHook)
        plan_builder.hooks.add(SaveDataSourceManifestHook)
        plan_builder.hooks.add(SaveWorkbookManifestHook)
        # plan_builder.hooks.add(LogMigrationActionsHook)

        ### Add filters here.
        self.logger.info("Adding Filters...")
        # plan_builder.filters.add(SkipProjectByParentLocationFilter)
        # plan_builder.filters.add(SkipDataSourceByParentLocationFilter)
        # plan_builder.filters.add(SkipWorkbooksByParentLocationFilter)
        plan_builder.filters.add(MigrateSpecificUsers)
        # plan_builder.filters.add(MigrateTaggedDataSources)
        plan_builder.filters.add(MigrateTaggedWorkbooks)

        ### SKIP FILTERS: These will skip ALL content.
        ### Uncomment when necessary, or when testing mappings/etc.
        # plan_builder.filters.add(SkipAllUsersFilter)
        plan_builder.filters.add(SkipAllGroupsFilter)
        plan_builder.filters.add(SkipAllProjectsFilter)
        plan_builder.filters.add(SkipAllDataSourcesFilter)
        # plan_builder.filters.add(SkipAllWorkbooksFilter)
        plan_builder.filters.add(SkipAllExtractRefreshTasksFilter)
        plan_builder.filters.add(SkipAllCustomViewsFilter)

        ### Add mappings here.
        self.logger.info("Adding Mappings...")
        # plan_builder.mappings.add(ProjectWithinSkippedLocationMapping)
        # plan_builder.mappings.add(DataSourceWithinSkippedLocationMapping)
        # plan_builder.mappings.add(WorkbookWithinSkippedLocationMapping)
        # plan_builder.mappings.add(MapDataSourcesToDefault)
        # plan_builder.mappings.add(MapWorkbooksToDefault)
        # plan_builder.mappings.add(UsernameMapping)

        ### Add transformers here.
        self.logger.info("Adding Transformers...")
        plan_builder.transformers.add(SetHiddenViews)
        # plan_builder.transformers.add(RemoveMissingDestinationUsersFromGroups)
        # plan_builder.transformers.add(UnlicensedUserToViewer)
        # plan_builder.transformers.add(UseRemoteQueryAgentDatasource)
        # plan_builder.transformers.add(UseRemoteQueryAgentWorkbook)
        # plan_builder.transformers.add(EncryptDataSourceExtracts)
        # plan_builder.transformers.add(EncryptWorkbookExtracts)
        # plan_builder.transformers.add(TransformScheduleStartTime)

        # Load manifest if available
        self.logger.info("Loading the previous manifest, if applicable.")
        prev_manifest = self.load_manifest(f"{manifest_path}")

        validation_result = plan_builder.validate()
        logging.info(f"Migration Plan validation result: {validation_result}")

        start_time = t.time()

        # Check if user wants to begin migration, if not, exit.
        begin_migration = input(
            "Migration plan is ready to build. Begin migration? (Y/n)"
        ).upper()

        if begin_migration.upper() == "Y":

            # Run the migration.
            self.logger.info("Building the Migration Plan")
            plan = plan_builder.build()

            self.logger.info("Executing the Migration Plan")
            results = migration.execute(plan, prev_manifest)

            end_time = t.time()

            # Save the manifest.
            self.logger.info("Saving the Migration manifest.")
            serializer.save(results.manifest, f"{manifest_path}")

            self.print_result(results)

            self.logger.info(f"Migration Started: {t.ctime(start_time)}")
            self.logger.info(f"Migration Ended: {t.ctime(end_time)}")
            self.logger.info(f"Elapsed: {end_time - start_time}")

            print("All done. Exiting.")

            self.done = True

        else:
            # User selected not to begin the migration, exit the program.
            self.logger.info(
                "User terminated migration before running the process. Exiting the application"
            )
            print("You have selected to not begin the migration. Exiting.")

            self.done = True


if __name__ == "__main__":

    program = Program()

    # Create a thread that will run the migration and start it.
    thread = Thread(target=program.migrate)
    thread.start()

    # Create a busy-wait loop to continue checking if Ctrl+C was pressed to cancel the migration.
    while not program.done:
        try:
            thread.join(1)
            program.done = True

        except KeyboardInterrupt:
            # Ctrl+C was caught, request migration to cancel.
            print("Caught Ctrl+C, shutting down...")

            # This will cause the Migration SDK to cleanup and finish,
            # which will cause the thread to finish.
            tableau_migration.cancellation_token_source.Cancel()

            # Wait for the migration thread to finish and then quit the application.
            thread.join()
            program.done = True
