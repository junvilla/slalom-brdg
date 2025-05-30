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
    LicenseLevels,
    TableauCloudUsernameMappingBase,
)

config = configparser.ConfigParser()
config.read('config.ini')

class TableauServerUsernameMapping(ContentMappingBase[IUser]):
    """Mapping that takes a username and maps it to the same user (Tableau Server ONLY)."""

    def __init__(self):
        """Default init to set up logging."""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)


    def map(
        self, ctx: ContentMappingContext[IUser]
    ) -> ContentMappingContext[IUser]:  # noqa: N802
        parent_domain = ctx.mapped_location.parent()

        item_name: str = ctx.content_item.name
        # item_name = item_name.replace(" ", "")

        ctx = ctx.map_to(parent_domain.append(item_name))
        self._logger.debug(
            "Mapped %s to %s", ctx.content_item.name, str(ctx.mapped_location)
        )

        return ctx