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

"""Filters for the Python.TestApplication."""

import configparser
import logging

from typing import Generic, TypeVar

from tableau_migration import (
    ContentFilterBase,
    ContentMigrationItem,
    IDataSource,
    IGroup,
    IProject,
    IUser,
    IWorkbook,
    IServerExtractRefreshTask,
    ICustomView,
    LicenseLevels,
)

config = configparser.ConfigParser()
config.read("config.ini")

TContent = TypeVar("TContent")


class SpecialUserFilter(ContentFilterBase[IUser]):
    """A class to filter (skip) special users."""

    def should_migrate(self, item: ContentMigrationItem[IUser]) -> bool:  # noqa: N802
        # Need to improve this to be an array not a single item
        if item.source_item.email in config["SPECIAL_USERS"]["EMAILS"]:
            logging.debug(
                "%s filtered %s", self.__class__.__name__, item.SourceItem.Email
            )
            return False

        return True


class UnlicensedUserFilter(ContentFilterBase[IUser]):
    """A class to filter (skip) unlicensed users."""

    def should_migrate(self, item: ContentMigrationItem[IUser]) -> bool:  # noqa: N802
        if item.source_item.license_level == LicenseLevels.UNLICENSED:
            logging.debug(
                "%s filtered %s", self.__class__.__name__, item.source_item.email
            )
            return False

        return True


class SkipAllUsersFilter(ContentFilterBase[IUser]):  # noqa: N801
    """A class to filter (skip) all users."""

    def should_migrate(self, item: ContentMigrationItem[IUser]) -> bool:  # noqa: N802
        logging.debug(
            "%s is filtering %s", self.__class__.__name__, item.source_item.name
        )
        return False


class SkipAllGroupsFilter(ContentFilterBase[IGroup]):  # noqa: N801
    """A class to filter (skip) all groups."""

    def should_migrate(self, item: ContentMigrationItem[IGroup]):  # noqa: N802
        logging.debug(
            "%s is filtering %s", self.__class__.__name__, item.source_item.name
        )
        return False


class SkipAllProjectsFilter(ContentFilterBase[IProject]):  # noqa: N801
    """A class to filter (skip) all projects."""

    def should_migrate(self, item: ContentMigrationItem[IProject]):  # noqa: N802
        logging.debug(
            "%s is filtering %s", self.__class__.__name__, item.source_item.name
        )
        return False


class SkipAllDataSourcesFilter(ContentFilterBase[IDataSource]):  # noqa: N801
    """A class to filter (skip) all data sources."""

    def should_migrate(self, item: ContentMigrationItem[IDataSource]):  # noqa: N802
        logging.debug(
            "%s is filtering %s", self.__class__.__name__, item.source_item.name
        )
        return False


class SkipAllWorkbooksFilter(ContentFilterBase[IWorkbook]):  # noqa: N801
    """A class to filter (skip) all workbooks."""

    def should_migrate(self, item: ContentMigrationItem[IWorkbook]):  # noqa: N802
        logging.debug(
            "%s is filtering %s", self.__class__.__name__, item.source_item.name
        )
        return False


class SkipAllExtractRefreshTasksFilter(
    ContentFilterBase[IServerExtractRefreshTask]
):  # noqa: N801
    """A class to filter (skip) all extract refresh tasks."""

    def should_migrate(
        self, item: ContentMigrationItem[IServerExtractRefreshTask]
    ) -> bool:
        logging.debug(
            '%s is filtering "%s"', self.__class__.__name__, item.source_item.name
        )
        return False


class SkipAllCustomViewsFilter(ContentFilterBase[ICustomView]):  # noqa: N801
    """A class to filter (skip) all custom views."""

    def should_migrate(self, item: ContentMigrationItem[ICustomView]) -> bool:
        logging.debug(
            '%s is filtering "%s"', self.__class__.__name__, item.source_item.name
        )
        return False


class _SkipContentByParentLocationFilter(Generic[TContent]):  # noqa: N801
    """Generic base filter wrapper to filter (skip) content by parent location."""

    def should_migrate(self, item: ContentMigrationItem[TContent], services) -> bool:
        if (
            item.source_item.location.parent().path
            != config["FILTERS"]["SKIPPED_PROJECT"]
        ):
            return True

        source_project_finder = services.get_source_finder(IProject)

        content_reference = source_project_finder.find_by_source_location(
            item.source_item.location.parent()
        )

        logging.info(
            'Skipping %s that belongs to "%s" (Project ID: %s)',
            self.__orig_class__.__args__[0].__name__,
            config["FILTERS"]["SKIPPED_PROJECT"],
            content_reference.id,
        )
        return False


class SkipProjectByParentLocationFilter(ContentFilterBase[IProject]):  # noqa: N801
    """A class to filter projects from a given parent location."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._filter = _SkipContentByParentLocationFilter[IProject](
            self.__class__.__name__
        )

    def should_migrate(self, item: ContentMigrationItem[IProject]) -> bool:
        return self._filter.should_migrate(item, self.services)


class SkipDataSourceByParentLocationFilter(
    ContentFilterBase[IDataSource]
):  # noqa: N801
    """A class to filter data sources from a given parent location."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._filter = _SkipContentByParentLocationFilter[IDataSource](
            self.__class__.__name__
        )

    def should_migrate(self, item: ContentMigrationItem[IDataSource]) -> bool:
        return self._filter.should_migrate(item, self.services)


class SkipWorkbooksByParentLocationFilter(ContentFilterBase[IWorkbook]):  # noqa: N801
    """A class to filter workbooks from a given parent location."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._filter = _SkipContentByParentLocationFilter[IWorkbook](
            self.__class__.__name__
        )

    def should_migrate(self, item: ContentMigrationItem[IWorkbook]) -> bool:
        return self._filter.should_migrate(item, self.services)


class MigrateSpecificUsers(ContentFilterBase[IUser]):  # noqa: N801
    """A class to filter all users not in the config variable user_list."""

    def should_migrate(self, item: ContentMigrationItem[IUser]):  # noqa: N802
        if item.source_item.name not in config["FILTERS"]["USER_LIST"]:
            logging.debug(
                "%s is filtering %s", self.__class__.__name__, item.source_item.name
            )
            return False

        return True


class MigrateContentByTag(ContentFilterBase[TContent]):  # noqa: N801
    """Generic base filter wrapper to migrate content by tag."""

    def should_migrate(self, item: ContentMigrationItem[TContent]) -> bool:
        migrate_tag = config["FILTERS"]["MIGRATE_TAG"]

        for tag in item.source_item.tags:
            if str(tag.label).strip().lower() == migrate_tag.strip().lower():
                return True

        logging.info(
            "Skipping %s - no matching content tag found.",
            item.source_item.name,
        )
        return False


class MigrateTaggedDataSources(MigrateContentByTag[IDataSource]):  # noqa: N801
    """A class to migrate data sources with a given tag."""

    pass


class MigrateTaggedWorkbooks(MigrateContentByTag[IWorkbook]):  # noqa: N801
    """A class to migrate workbooks with a given tag."""

    pass
