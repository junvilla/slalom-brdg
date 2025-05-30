import configparser
import logging
from typing import TypeVar
from tableau_migration import (
    ContentMappingBase,
    ContentMappingContext,
    IProject,
    IDataSource,
    IWorkbook,
    )

TContent = TypeVar("TContent")

class UpdateContentOwnership(ContentMappingBase[TContent]):
    """Updates the owner of content."""

    def __init__(self):
        """Default init to set up logging."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)

    def map(self, ctx: ContentMappingContext[IProject]) -> ContentMappingContext[IProject]:
        owner = ctx.content_item.owner

        return ctx
    
class UpdateProjectOwner(UpdateContentOwnership[IProject]):
    """A transformer that updates the owner of a project."""
    pass

class UpdateDatasourceOwner(UpdateContentOwnership[IDataSource]):
    """A transformer that updates the owner of a data source."""
    pass

class UpdateWorkbookOwner(UpdateContentOwnership[IWorkbook]):
    """A transformer that updates the owner of a workbook."""
    pass