# Copyright (c) 2024, Salesforce, Inc.
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

import os
import ast
import configparser
import logging
import pandas as pd
from datetime import time
from typing import TypeVar
from tableau_migration import (
    ContentTransformerBase,
    ICloudExtractRefreshTask,
    IPublishableDataSource,
    IPublishableWorkbook,
    IPublishableCustomView,
    IPublishableGroup,
    IUser,
    ITag,
    LicenseLevels,
)
from Shared_TSC_GlobalVariables import file_loc


config = configparser.ConfigParser()
config.read("config.ini")

# Load the list of Workbooks with hidden views
hidden_view_file = os.path.join(file_loc, "HiddenViewList.csv")
hidden_view_df = pd.read_csv(hidden_view_file)

TContent = TypeVar("TContent")


class CustomViewDefaultUsers(ContentTransformerBase[IPublishableCustomView]):
    """A class to transform and pass a list of default users for Custom Views."""

    # Pass in list of users retrieved from Users API
    default_users = []

    def transform(
        self, item_to_transform: IPublishableCustomView
    ) -> IPublishableCustomView:
        item_to_transform.default_users = self.default_users
        return item_to_transform


class SetHiddenViews(ContentTransformerBase[IPublishableWorkbook]):
    """A class to set views to hidden on Workbooks, since this isn't handled by default."""

    def transform(
        self, item_to_transform: IPublishableWorkbook
    ) -> IPublishableWorkbook:

        # Filter the hidden_view_df by the Workbook Id
        logging.info(
            f"Checking for hidden views for [{item_to_transform.id}] {item_to_transform.name}"
        )
        hidden_views = hidden_view_df[
            hidden_view_df["Workbook Id"] == str(item_to_transform.id)
        ].reset_index(drop=True)

        if hidden_views.empty:
            logging.info(f"Workbook [{item_to_transform.name}] has no hidden views.")
            return item_to_transform

        else:
            view_list = ast.literal_eval(hidden_views.iloc[0]["Hidden Views"])
            logging.info(
                f"Setting Workbook [{item_to_transform.name}] views to hidden: {view_list}"
            )
            item_to_transform.hidden_view_names = view_list
            return item_to_transform


class UnlicensedUserToViewer(ContentTransformerBase[IUser]):
    """A class to transform unlicensed users to Viewers."""

    def transform(self, item_to_transform: IUser) -> IUser:
        if item_to_transform.license_level == LicenseLevels.UNLICENSED:
            item_to_transform.license_level = LicenseLevels.VIEWER
            logging.debug(
                "Mapped %s to %s", item_to_transform.email, LicenseLevels.VIEWER
            )

        return item_to_transform


class RemoveMissingDestinationUsersFromGroups(
    ContentTransformerBase[IPublishableGroup]
):
    """A class to transform groups to not try to link skipped users to the group."""

    def transform(self, item_to_transform: IPublishableGroup) -> IPublishableGroup:
        destination_user_finder = self.services.get_destination_finder(IUser)
        users_list = []
        for usergroup in item_to_transform.users:
            destination_reference = destination_user_finder.find_by_id(
                usergroup.user.id
            )

            if destination_reference is not None:
                users_list.append(usergroup)

        item_to_transform.users = users_list

        return item_to_transform


class UseRemoteQueryAgent(ContentTransformerBase[TContent]):
    """Update a Data Source or Workbook extract to use the Remote Query Agent (Tableau Bridge)."""

    # Populate local_sources with a comma-separated list of on-prem data types
    # e.g. ["sqlserver", "oracle", "snowflake", "redshift"]
    local_sources = []

    def transform(self, item_to_transform: TContent) -> TContent:
        # Get the list of connections for the data source
        connections = item_to_transform.connections

        # Check for local/on-premises data connections
        check = False

        for connection in connections:
            if connection.type in self.local_sources:
                check = True

        # If connections contains a local source, use remote query agent (Tableau Bridge)
        if check:
            item_to_transform.use_remote_query_agent = True

        return item_to_transform


class UseRemoteQueryAgentDatasource(UseRemoteQueryAgent[IPublishableDataSource]):
    """A transformer that sets a data source to use Tableau Bridge (remote query agent)."""

    pass


class UseRemoteQueryAgentWorkbook(UseRemoteQueryAgent[IPublishableWorkbook]):
    """A transformer that sets a workbook to use Tableau Bridge (remote query agent)."""

    pass


class AddMigratedTag(ContentTransformerBase[TContent]):
    """A transformer that adds the "Migrated" tag to items."""

    def transform(self, itemToTransform: TContent) -> TContent:
        tag: str = "Migrated"

        itemToTransform.tags.append(ITag(tag))

        return itemToTransform


class MigratedTagTransformerForDataSources(AddMigratedTag[IPublishableDataSource]):
    """A transformer that adds the "Migrated" tag to data sources."""

    pass


class MigratedTagTransformerForWorkbooks(AddMigratedTag[IPublishableWorkbook]):
    """A transformer that adds the "Migrated" tag to workbooks."""

    pass


class EncryptExtracts(ContentTransformerBase[TContent]):
    """A transformer that enables extract encryption."""

    def transform(self, item_to_transform: TContent) -> TContent:
        item_to_transform.encrypt_extracts = True

        return item_to_transform


class EncryptDataSourceExtracts(EncryptExtracts[IPublishableDataSource]):
    """A transformer that sets data sources to encrypt extracts."""

    pass


class EncryptWorkbookExtracts(EncryptExtracts[IPublishableWorkbook]):
    """A transformer that sets workbooks to encrypt extracts."""

    pass


class TransformScheduleStartTime(ContentTransformerBase[ICloudExtractRefreshTask]):
    """A transformer to adjust the start time of an extract refresh task."""

    def transform(
        self, item_to_transform: ICloudExtractRefreshTask
    ) -> ICloudExtractRefreshTask:
        # In this example, the start time is in UTC.
        if item_to_transform.schedule.frequency_details.start_at:
            prev_start_at = item_to_transform.schedule.frequency_details.start_at

            # convert the start time to EDT
            item_to_transform.schedule.frequency_details.start_at = time(
                prev_start_at.hour - 4,
                prev_start_at.minute,
                prev_start_at.second,
                prev_start_at.microsecond,
            )

        return item_to_transform
