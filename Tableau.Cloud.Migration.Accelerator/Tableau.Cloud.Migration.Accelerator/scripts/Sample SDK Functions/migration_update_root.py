import logging
from typing import Generic, TypeVar
from tableau_migration import (
    ContentLocation,
    ContentMappingBase,
    ContentMappingContext,
    IDataSource,
    IProject,
    IWorkbook,
)

def replace_datasource_project(original_list, original_project, new_project):
    """Renames original_project to new_project within original_list."""
    modified_list = [
        new_project if item == original_project else item for item in original_list
    ]

    return modified_list

TContent = TypeVar("TContent")


class _TopLevelProjectMapping(Generic[TContent]):
    """Generic base wrapper to update an object's parent project based on the parent_project variable in config.ini"""

    def __init__(self, logger_name: str):
        """Default init to set up logging."""
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

    def map(
        self, ctx: ContentMappingContext[TContent]
    ) -> ContentMappingContext[TContent]:
        """Executes the mapping.

        Args:
            ctx: The input context from the migration engine or previous hook.

        Returns:
            The context, potentially modified to pass on to the next hook or migration engine,
            or None to continue passing the input context.
        """
        # Get the location path_separator and path_segments for the content item.
        path_separator = ctx.content_item.location.path_separator
        path_segments = ctx.content_item.location.path_segments

        # Map the new top-level project based on the current top-level project
        if (
            ctx.content_item.location.path_segments[0] == ".Sandbox"
            or ctx.content_item.location.name == ".Sandbox"
        ):
            path_segments[0] = "Sandbox"

        elif (
            ctx.content_item.location.path_segments[0] == ".Staging Area"
            or ctx.content_item.location.name == ".Staging Area"
        ):
            path_segments[0] = "Sandbox"
            path_segments.insert(1, "Sales Sandbox")
            path_segments.insert(2, "Un-Sorted Sales Sandbox")
            path_segments.insert(3, "Staging Area")

        elif (
            ctx.content_item.location.path_segments[0] == ".To Delete"
            or ctx.content_item.location.name == ".To Delete"
        ):
            path_segments[0] = ".Archived"

        elif (
            ctx.content_item.location.path_segments[0] == "Default"
            or ctx.content_item.location.name == "Default"
        ):
            path_segments[0] = "default"

        elif (
            ctx.content_item.location.path_segments[0] == "Data Sources"
            or ctx.content_item.location.name == "Data Sources"
        ):
            if (
                ctx.content_item.name == "Datasource: Accounting"
                or "Datasource: Accounting" in path_segments
                or ctx.content_item.location.name == "Datasource: Accounting"
            ):
                path_segments[0] = "Accounting Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Accounting", ".Datasource: Accounting"
                )

            if (
                ctx.content_item.name == "Datasource: Construction"
                or "Datasource: Construction" in path_segments
                or ctx.content_item.location.name == "Datasource: Construction"
            ):
                path_segments[0] = "Construction Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Construction", ".Datasource: Construction"
                )

            if (
                ctx.content_item.name == "Datasource: Division Hierarchy"
                or "Datasource: Division Hierarchy" in path_segments
                or ctx.content_item.location.name == "Datasource: Division Hierarchy"
            ):
                path_segments[0] = "SHE Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Division Hierarchy", ".Datasource: Division Hierarchy"
                )

            if (
                ctx.content_item.name == "Datasource: Finance"
                or "Datasource: Finance" in path_segments
                or ctx.content_item.location.name == "Datasource: Finance"
            ):
                path_segments[0] = "Finance Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Finance", ".Datasource: Finance"
                )

            if (
                ctx.content_item.name == "Datasource: IT"
                or "Datasource: IT" in path_segments
                or ctx.content_item.location.name == "Datasource: IT"
            ):
                path_segments[0] = "IT Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: IT", ".Datasource: IT"
                )

            if (
                ctx.content_item.name == "Datasource: Logistics"
                or "Datasource: Logistics" in path_segments
                or ctx.content_item.location.name == "Datasource: Logistics"
            ):
                path_segments[0] = "Logistics Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Logistics", ".Datasource: Logistics"
                )

            if (
                ctx.content_item.name == "Datasource: MSS Internal"
                or "Datasource: MSS Internal" in path_segments
                or ctx.content_item.location.name == "Datasource: MSS Internal"
            ):
                path_segments[0] = "MSS Internal Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: MSS Internal", ".Datasource: MSS Internal"
                )

            if (
                ctx.content_item.name == "Datasource: Operations Reporting"
                or "Datasource: Operations Reporting" in path_segments
                or ctx.content_item.location.name == "Datasource: Operations Reporting"
            ):
                path_segments[0] = "Operations Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Operations Reporting", ".Datasource: Operations Reporting"
                )

            if (
                ctx.content_item.name == "Datasource: Sales"
                or "Datasource: Sales" in path_segments
                or ctx.content_item.location.name == "Datasource: Sales"
            ):
                path_segments[0] = "Sales Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Sales", ".Datasource: Sales"
                )

            if (
                ctx.content_item.name == "Datasource: Sales \u002B Logistics"
                or "Datasource: Sales \u002B Logistics" in path_segments
                or ctx.content_item.location.name == "Datasource: Sales \u002B Logistics"
            ):
                path_segments[0] = "Sales Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Sales \u002B Logistics", ".Datasource: Sales \u002B Logistics"
                )

            if (
                ctx.content_item.name == "Datasource: SHE"
                or "Datasource: SHE" in path_segments
                or ctx.content_item.location.name == "Datasource: SHE"
            ):
                path_segments[0] = "SHE Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: SHE", ".Datasource: SHE"
                )

            if (
                ctx.content_item.name == "Datasource: Strategic Sourcing"
                or "Datasource: Strategic Sourcing" in path_segments
                or ctx.content_item.location.name == "Datasource: Strategic Sourcing"
            ):
                path_segments[0] = "Strategic Sourcing Reporting"
                path_segments.insert(0, "Productionalized Reporting")
                path_segments = replace_datasource_project(
                    path_segments, "Datasource: Strategic Sourcing", ".Datasource: Strategic Sourcing"
                )

            # print("\nName: ", ctx.content_item.name, "\nLocation Name: ", ctx.content_item.location.name, "\nPath Segments: ", path_segments)

        elif (ctx.content_item.name != "Productionalized Reporting"):
            # Build the new project location.
            path_segments.insert(0, "Productionalized Reporting")

        self._logger.info(
            'Mapping %s "%s" to top-level project "%s".',
            self.__orig_class__.__args__[0].__name__,
            ctx.content_item.name,
            ctx.content_item.location.path_segments[0],
        )

        ctx = ctx.map_to(
            ContentLocation.from_path(
                path_separator.join(path_segments), path_separator
            )
        )

        return ctx


class UpdateTopLevelProjectforChildProject(ContentMappingBase[IProject]):
    """A class to map projects to a new parent project specified in config.ini"""

    def __init__(self):
        """Default init to set up wrapper."""
        self._mapper = _TopLevelProjectMapping[IProject](self.__class__.__name__)

    def map(
        self, ctx: ContentMappingContext[IProject]
    ) -> ContentMappingContext[IProject]:
        return self._mapper.map(ctx)


class UpdateTopLevelProjectForWorkbook(ContentMappingBase[IWorkbook]):
    """A class to map workbooks to a new project specified in config.ini"""

    def __init__(self):
        """Default init to set up wrapper."""
        self._mapper = _TopLevelProjectMapping[IWorkbook](self.__class__.__name__)

    def map(
        self, ctx: ContentMappingContext[IWorkbook]
    ) -> ContentMappingContext[IWorkbook]:
        return self._mapper.map(ctx)


class UpdateTopLevelProjectForDatasource(ContentMappingBase[IDataSource]):
    """A class to map data sources to a new project specified in config.ini"""

    def __init__(self):
        """Default init to set up wrapper."""
        self._mapper = _TopLevelProjectMapping[IDataSource](self.__class__.__name__)

    def map(
        self, ctx: ContentMappingContext[IDataSource]
    ) -> ContentMappingContext[IDataSource]:
        return self._mapper.map(ctx)
