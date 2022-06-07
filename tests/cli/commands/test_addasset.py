import os
import shutil
from tempfile import TemporaryDirectory

import pystac
from pystac.utils import make_absolute_href

from stactools.cli.commands.addasset import create_addasset_command
from stactools.core import move_all_assets
from stactools.testing import CliTestCase
from tests import test_data

from .test_cases import TestCases


def create_temp_catalog_copy(tmp_dir):
    col = TestCases.planet_disaster()
    col.normalize_hrefs(tmp_dir)
    col.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    move_all_assets(col, copy=True)
    col.save()

    return col


def create_temp_copy(src_path, tmp_dir, target_name):
    temp_path = os.path.join(tmp_dir, target_name)
    shutil.copyfile(src_path, temp_path)
    return temp_path


class AddAssetTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_addasset_command]

    def test_add_asset_to_item(self):
        with TemporaryDirectory() as tmp_dir:
            catalog = create_temp_catalog_copy(tmp_dir)
            items = list(catalog.get_all_items())
            item = list(catalog.get_all_items())[0]
            asset = item.get_assets().get("test-asset")
            assert asset is None
            item_path = make_absolute_href(
                items[0].get_self_href(), catalog.get_self_href()
            )

            asset_path = test_data.get_path("data-files/core/byte.tif")
            cmd = [
                "addasset",
                item_path,
                "test-asset",
                asset_path,
                "--title",
                "test",
                "--description",
                "placeholder asset",
                "--roles",
                "thumbnail",
                "--roles",
                "overview",
            ]
            self.run_command(cmd)

            updated = pystac.read_file(catalog.get_self_href())
            item = list(updated.get_all_items())[0]
            asset = item.get_assets().get("test-asset")
            assert isinstance(asset, pystac.Asset), asset
            assert asset.href is not None, asset.to_dict()
            assert os.path.isfile(asset.href), asset.to_dict()
            assert asset.title == "test", asset.to_dict()
            assert asset.description == "placeholder asset", asset.to_dict()
            self.assertListEqual(asset.roles, ["thumbnail", "overview"])

    def add_asset_move(self):
        with TemporaryDirectory() as tmp_dir:
            catalog = create_temp_catalog_copy(tmp_dir)
            items = list(catalog.get_all_items())
            item = list(catalog.get_all_items())[0]
            asset = item.get_assets().get("test-asset")
            assert asset is None
            item_path = make_absolute_href(
                items[0].get_self_href(), catalog.get_self_href()
            )
            with TemporaryDirectory as tmp_dir2:
                asset_path = create_temp_copy(
                    test_data.get_path("data-files/core/byte.tif"), tmp_dir2, "test.tif"
                )
                cmd = [
                    "addasset",
                    item_path,
                    "test-asset",
                    asset_path,
                    "--title",
                    "test",
                    "--description",
                    "placeholder asset",
                    "--move-assets",
                    "--ignore-conflicts",
                ]
                self.run_command(cmd)

                updated = pystac.read_file(catalog.get_self_href())
                item = list(updated.get_all_items())[0]
                asset = item.get_assets().get("test-asset")
                assert isinstance(asset, pystac.Asset), asset
                assert asset.href is not None, asset.to_dict()
                assert os.path.isfile(asset.href), asset.to_dict()
                assert asset.title == "test", asset.to_dict()
                assert asset.description == "placeholder asset", asset.to_dict()
                self.assertEqual(
                    os.path.dirname(asset.get_absolute_href()),
                    os.path.dirname(item.get_self_href()),
                )
