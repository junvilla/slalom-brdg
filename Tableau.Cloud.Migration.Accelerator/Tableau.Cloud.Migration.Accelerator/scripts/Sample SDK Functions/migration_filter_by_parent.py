import configparser
import logging
from typing import Generic, TypeVar

from tableau_migration import (
    ContentFilterBase,
    ContentMigrationItem,
    IDataSource,
    IProject,
    IWorkbook,
)

config = configparser.ConfigParser()
config.read('config.ini')

TContent = TypeVar("TContent")

class _MigrateByProject(Generic[TContent]):  # noqa: N801
    """Generic base filter wrapper to migrate by a specified Project name in the migrate_project config.ini variable."""

    def __init__(self, logger_name: str):
        """Default init to set up logging."""
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

    def should_migrate(self, item: ContentMigrationItem[TContent]) -> bool:
        container_segments = item.source_item.location.path_segments

        # root_project = container_segments[0] # for top-level project
        root_project = container_segments[-1] # for parent project

        if root_project == config["FILTERS"]["MIGRATE_PROJECT"]:
            return True

        self._logger.info(
            'Skipping [%s] %s - does not belong to Project: "%s"',
            self.__orig_class__.__args__[0].__name__,
            item.source_item.name,
            config['FILTERS']['MIGRATE_PROJECT']
        )
        return False


class MigrateProjectByNameFilter(ContentFilterBase[IProject]):  # noqa: N801
    """A class to migrate projects of a given name."""

    def __init__(self):
        """Default init to set up wrapper."""
        self._filter = _MigrateByProject[IProject](
            self.__class__.__name__
        )

    def should_migrate(self, item: ContentMigrationItem[IProject]) -> bool:
        return self._filter.should_migrate(item)
    

class _MigrateContentByProject(ContentFilterBase[TContent]):  # noqa: N801
    """Generic base filter wrapper to migrate content items by a specified 
       Project name in the migrate_project config.ini variable.
    """

    def __init__(self, logger_name: str):
        """Default init to set up logging."""
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

    def should_migrate(self, item: ContentMigrationItem[TContent]) -> bool:
        container_segments = item.source_item.location.path_segments

        # Go to next to last, since the last item is the content item name
        root_project = container_segments[-2]

        if root_project == config["FILTERS"]["MIGRATE_PROJECT"]:
            return True

        self._logger.info(
            'Skipping [%s] %s - does not belong to Project: "%s"',
            self.__orig_class__.__args__[0].__name__,
            item.source_item.name,
            config['FILTERS']['MIGRATE_PROJECT']
        )
        return False

class MigrateDatasourceByProjectFilter(_MigrateContentByProject[IDataSource]):  # noqa: N801
    """A class to migrate data sources from a given project."""
    pass

class MigrateWorkbookByProjectFilter(_MigrateContentByProject[IWorkbook]):  # noqa: N801
    """A class to migrate workbooks from a given project."""
    pass
