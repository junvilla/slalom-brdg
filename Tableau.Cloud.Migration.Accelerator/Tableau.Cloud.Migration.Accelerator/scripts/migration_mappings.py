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

import configparser
import logging
from typing import Generic, TypeVar
from tableau_migration import (
    ContentLocation,
    ContentMappingBase,
    ContentMappingContext,
    IDataSource,
    IProject,
    IUser,
    IWorkbook,
)

config = configparser.ConfigParser()
config.read("config.ini")

TContent = TypeVar("TContent")


class UsernameMapping(ContentMappingBase[IUser]):
    """Mapping that takes a username and maps it to an email address."""

    def __init__(self):
        """Default init to set up logging."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)

    def map(
        self, ctx: ContentMappingContext[IUser]
    ) -> ContentMappingContext[IUser]:  # noqa: N802
        domain = ctx.mapped_location.parent()

        self._logger.debug(
            "Mapped %s to %s", ctx.content_item.name, str(ctx.mapped_location)
        )

        return ctx.map_to(
            domain.append(ctx.content_item.name + "@" + config["USERS"]["EMAIL_DOMAIN"])
        )


class _ContentWithinSkippedLocationMapping(Generic[TContent]):
    """Generic base mapping wrapper for content within skipped location."""

    def __init__(self, logger_name: str):
        """Default init to set up logging."""
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

    def map(
        self, ctx: ContentMappingContext[TContent], services
    ) -> ContentMappingContext[TContent]:
        """Executes the mapping.

        Args:
            ctx: The input context from the migration engine or previous hook.

        Returns:
            The context, potentially modified to pass on to the next hook or migration engine, or None to continue passing the input context.
        """
        if config["FILTERS"]["SKIPPED_PROJECT"] == "":
            return ctx

        path_replaced = ctx.content_item.location.path.replace(
            config["FILTERS"]["SKIPPED_PROJECT"], ""
        )
        path_separator = ctx.content_item.location.path_separator

        if (
            not ctx.content_item.location.path.startswith(
                config["FILTERS"]["SKIPPED_PROJECT"]
            )
            or path_replaced == ""
            or len(path_replaced.split(path_separator)) <= 2
        ):  # considering the first empty value before the first slash
            return ctx

        destination_project_finder = services.get_destination_finder(IProject)

        mapped_destination = ContentLocation.from_path(
            config["FILTERS"]["SKIPPED_PARENT_DESTINATION"], path_separator
        )

        project_reference = destination_project_finder.find_by_mapped_location(
            mapped_destination
        )

        if project_reference is None:
            self._logger.error(
                'Cannot map %s "%s" that belongs to "%s" to the project "%s". You must create the destination location first.',
                self.__orig_class__.__args__[0].__name__,
                ctx.content_item.name,
                config["FILTERS"]["SKIPPED_PROJECT"],
                config["FILTERS"]["SKIPPED_PARENT_DESTINATION"],
            )
            return ctx

        mapped_list = list(mapped_destination.path_segments)

        for i in range(
            len(
                config["FILTERS"]["SKIPPED_PROJECT"].split(
                    ctx.content_item.location.path_separator
                )
            )
            + 1,
            len(ctx.content_item.location.path_segments),
        ):
            mapped_list.append(ctx.content_item.location.path_segments[i])

        self._logger.info(
            'Mapping the %s "%s" that belongs to "%s" to the project "%s" (Id: %s).',
            self.__orig_class__.__args__[0].__name__,
            ctx.content_item.name,
            config["FILTERS"]["SKIPPED_PROJECT"],
            config["FILTERS"]["SKIPPED_PARENT_DESTINATION"],
            project_reference.id,
        )

        ctx = ctx.map_to(
            ContentLocation.from_path(path_separator.join(mapped_list), path_separator)
        )

        return ctx


class ProjectWithinSkippedLocationMapping(ContentMappingBase[IProject]):
    """A class to map projects within a skipped project to a configured destination project."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._mapper = _ContentWithinSkippedLocationMapping[IProject](
            self.__class__.__name__
        )

    def map(
        self, ctx: ContentMappingContext[IProject]
    ) -> ContentMappingContext[IProject]:
        return self._mapper.map(ctx, self.services)


class DataSourceWithinSkippedLocationMapping(ContentMappingBase[IDataSource]):
    """A class to map datasources within a skipped project to a configured destination project."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._mapper = _ContentWithinSkippedLocationMapping[IDataSource](
            self.__class__.__name__
        )

    def map(
        self, ctx: ContentMappingContext[IDataSource]
    ) -> ContentMappingContext[IDataSource]:
        return self._mapper.map(ctx, self.services)


class WorkbookWithinSkippedLocationMapping(ContentMappingBase[IWorkbook]):
    """A class to map workbooks within a skipped project to a configured destination project."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._mapper = _ContentWithinSkippedLocationMapping[IWorkbook](
            self.__class__.__name__
        )

    def map(
        self, ctx: ContentMappingContext[IWorkbook]
    ) -> ContentMappingContext[IWorkbook]:
        return self._mapper.map(ctx, self.services)


class _MapLocationToDefault(ContentMappingBase[TContent]):
    """Generic base mapping wrapper to remap content to 'default' folder."""

    def map(
        self, ctx: ContentMappingContext[TContent]
    ) -> ContentMappingContext[TContent]:
        # Get the project location for the content item.
        container_location = ctx.content_item.location.parent()

        # Build the new project location.
        new_container_location = container_location.rename("Default")

        # Build the new content item location.
        new_location = new_container_location.append(ctx.content_item.name)

        # Map the new content item location.
        ctx = ctx.map_to(new_location)

        return ctx


class MapDataSourcesToDefault(_MapLocationToDefault[IDataSource]):
    """A function that maps a data source to the Default project."""

    pass


class MapWorkbooksToDefault(_MapLocationToDefault[IWorkbook]):
    """A function that maps a workbook to the Default project."""

    pass
