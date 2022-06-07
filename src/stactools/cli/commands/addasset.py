from typing import List, Optional

import click
import pystac

from stactools.core import add_asset_to_item


def add_asset(
    item_path: str,
    asset_key: str,
    asset_path: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    media_type: Optional[str] = None,
    roles: Optional[List[str]] = None,
    move_assets: bool = False,
    ignore_conflicts: bool = False,
) -> None:
    item = pystac.read_file(item_path)
    if not isinstance(item, pystac.Item):
        raise click.BadArgumentUsage(f"{item_path} is not a STAC Item")
    asset = pystac.Asset(asset_path, title, description, media_type, roles)
    item = add_asset_to_item(
        item,
        asset_key,
        asset,
        move_assets=move_assets,
        ignore_conflicts=ignore_conflicts,
    )
    item.save_object()


def create_addasset_command(cli: click.Group) -> click.Command:
    @cli.command("addasset", short_help="Add an asset to an item.")
    @click.argument("item_path")
    @click.argument("asset_key")
    @click.argument("asset_path")
    @click.option("--title", help="Optional title of the asset")
    @click.option(
        "--description",
        help=(
            "Optional description of the asset providing additional details, "
            "such as how it was processed or created."
        ),
    )
    @click.option(
        "--media-type", help="Optional description of the media type of the asset"
    )
    @click.option(
        "--roles", help="Optional, semantic roles of the asset", multiple=True
    )
    @click.option(
        "--move-assets",
        is_flag=True,
        help="Move asset to the target Item's location.",
    )
    @click.option(
        "--ignore-conflicts",
        is_flag=True,
        help=(
            "If there is a conflict with an existing asset, do not raise an "
            "error, leave the original asset from the target item in place."
        ),
    )
    def addasset_command(
        item_path: str,
        asset_key: str,
        asset_path: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        media_type: Optional[str] = None,
        roles: Optional[List[str]] = None,
        move_assets: bool = False,
        ignore_conflicts: bool = False,
    ) -> None:
        add_asset(
            item_path,
            asset_key,
            asset_path,
            title,
            description,
            media_type,
            roles,
            move_assets=move_assets,
            ignore_conflicts=ignore_conflicts,
        )

    return addasset_command
