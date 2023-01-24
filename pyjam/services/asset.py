import os

from pyjam.interfaces import IDisposable


class AssetService(IDisposable):
    def __init__(self):
        # a dict where the key is the AssetType and the value is another dict of that type of assets
        self._assets = {}

    @staticmethod
    def get_path_and_asset_key(fullpath: str) -> tuple:
        basename = os.path.basename(fullpath)
        filename_without_ext = os.path.splitext(basename)
        return os.path.dirname(fullpath), filename_without_ext[0]

    def get(self, path):
        path_and_asset_key = AssetService.get_path_and_asset_key(path)
        return self._assets[path_and_asset_key[0]][path_and_asset_key[1]]

    def insert(self, path, asset):
        path_and_asset_key = AssetService.get_path_and_asset_key(path)
        asset_dict = self._assets.get(path_and_asset_key[0])
        if asset_dict is None:
            asset_dict = {}
            self._assets[path_and_asset_key[0]] = asset_dict
        asset_dict[path_and_asset_key[1]] = asset

    def pop(self, path):
        path_and_asset_key = AssetService.get_path_and_asset_key(path)
        asset_dict = self._assets.get(path_and_asset_key[0])
        if asset_dict is not None:
            elem = asset_dict[path_and_asset_key[1]].pop()
            elem.dispose()
        else:
            raise KeyError()

    def dispose(self):
        pass
