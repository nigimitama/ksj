import os
import tempfile
import zipfile
from urllib.request import urlretrieve
import geopandas as gpd


def get_shp(file_url: str, save_dir: str, save_file_name=None,
            unzip=False, silent=False):
    """指定したURLのzipファイルを指定フォルダにダウンロードする。

    Args:
        file_url (str): 国土数値情報ダウンロードサービスが提供するzipファイルのURL
        save_dir (str): 保存先ディレクトリのパス
        save_file_name (str): 保存するzipファイルの名前（任意）
        unzip (bool): Trueの場合、zipファイルの解凍まで行います。
        silent (bool): Trueの場合、「どのファイルをどこに解凍したか」という表示を無効にします。

    Returns:
        None
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    save_file_name = os.path.basename(
        file_url) if save_file_name is None else save_file_name
    save_path = os.path.join(save_dir, save_file_name)
    urlretrieve(url=file_url, filename=save_path)
    if not silent:
        print(f"{save_file_name} is saved at {save_dir}")
    if unzip:
        with zipfile.ZipFile(save_path) as existing_zip:
            existing_zip.extractall(save_dir)
        if not silent:
            print(f"{save_file_name} is extracted to {save_dir}")


def read_shp(file_url, save_dir=None,
             save_file_name=None, silent=False) -> gpd.GeoDataFrame:
    """
    指定したURLのzipファイルを指定フォルダあるいは
    一時フォルダにダウンロードし、解凍してgeopandasで開く

    Args:
        file_url (str): 国土数値情報ダウンロードサービスが提供するzipファイルのURL
        save_dir (str): 保存先ディレクトリのパス
        save_file_name (str): 保存するzipファイルの名前（任意）
        silent (bool): Trueの場合、「どのファイルをどこに解凍したか」という表示を無効にします。

    Returns:
        シェープファイルのデータ（geopandas.GeoDataFrame）
    """
    if save_file_name is None:
        save_file_name = os.path.basename(file_url)
    if save_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        save_dir = temp_dir.name
    elif not os.path.exists(save_dir):
        os.mkdir(save_dir)
    save_path = os.path.join(save_dir, save_file_name)
    urlretrieve(url=file_url, filename=save_path)
    if not silent:
        print(f"{save_file_name} is extracted to {save_dir}")
    # extract to save_dir
    with zipfile.ZipFile(save_path) as existing_zip:
        existing_zip.extractall(save_dir)
    # load
    file_names = _get_files(save_dir)
    shapefiles = [file_name for file_name in file_names if ".shp" in file_name]
    modify_times = [os.lstat(shapefile).st_mtime for shapefile in shapefiles]
    sorted_indices = sorted(range(len(modify_times)),
                            key=lambda k: modify_times[k], reverse=True)
    newest_mod_file = shapefiles[sorted_indices[0]]
    file_path = os.path.join(save_dir, newest_mod_file)
    print(f"Reading a shapefile from {file_path}")
    shape_file = gpd.read_file(file_path)
    if save_dir is None:
        temp_dir.cleanup()
    return shape_file


def _get_files(path: str) -> list:
    """get file pathes recursively"""
    file_names = []
    for (root, _, files) in os.walk(path):
        for f in files:
            file_names.append(os.path.join(root, f))
    return file_names
