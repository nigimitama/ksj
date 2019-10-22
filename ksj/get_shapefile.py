import os
import tempfile
import zipfile
from urllib.request import urlretrieve
import geopandas as gpd


def get_shp(file_url: str, save_dir: str, save_file_name=None,
            unzip=False, silent=False):
    """指定したURLのzipファイルを指定フォルダにダウンロードする。

    Parameters
    ----------
    file_url : str
        国土数値情報ダウンロードサービスが提供するzipファイルのURL
    save_dir : str
        保存先ディレクトリのパス
    save_file_name : str
        保存するzipファイルの名前
    unzip : bool
        Trueの場合、zipファイルの解凍まで行います。
    silent : bool
        Trueの場合、ファイルをどこに解凍したかについての表示を無効にします。

    Returns
    -------
    None
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if save_file_name is None:
        save_file_name = os.path.basename(file_url)
    save_path = os.path.join(save_dir, save_file_name)
    urlretrieve(url=file_url, filename=save_path)
    if not silent:
        print(f"{save_file_name} is saved at {save_dir}")
    if unzip:
        name_without_extension = os.path.splitext(save_file_name)[0]
        extract_dir = os.path.join(save_dir, name_without_extension)
        if not os.path.exists(extract_dir):
            os.mkdir(extract_dir)
        with zipfile.ZipFile(save_path) as existing_zip:
            existing_zip.extractall(extract_dir)
        if not silent:
            print(f"{save_file_name} is extracted to {extract_dir}")


def read_shp(file_url, save_dir=None,
             save_file_name=None, silent=True) -> gpd.GeoDataFrame:
    """
    指定したURLのzipファイルを指定フォルダあるいは一時フォルダにダウンロードし、
    解凍してgeopandasで開く

    Parameters
    ----------
    file_url : str
        国土数値情報ダウンロードサービスが提供するzipファイルのURL
    save_dir : str
        保存先ディレクトリのパス
    save_file_name : str
        保存するzipファイルの名前（任意）
    silent : bool
        Trueの場合、ファイルをどこに解凍したかについての表示を無効にします。

    Returns
    -------
    geopandas.GeoDataFrame
        シェープファイルのデータ
    """
    if save_file_name is None:
        save_file_name = os.path.basename(file_url)
    if save_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        save_dir = temp_dir.name
    elif not os.path.exists(save_dir):
        os.mkdir(save_dir)
    save_path = os.path.join(save_dir, save_file_name)
    # download
    urlretrieve(url=file_url, filename=save_path)
    # unzip
    name_without_extension = os.path.splitext(save_file_name)[0]
    extract_dir = os.path.join(save_dir, name_without_extension)
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)
    with zipfile.ZipFile(save_path) as existing_zip:
        existing_zip.extractall(extract_dir)
    if not silent:
        print(f"{save_file_name} is extracted to {extract_dir}")
    # load
    file_names = _get_files(extract_dir)
    shapefiles = [file_name for file_name in file_names if ".shp" in file_name]
    if len(shapefiles) > 1:
        # 複数.shpがある場合、更新日時が最新のものを使う
        modify_times = [os.lstat(shp).st_mtime for shp in shapefiles]
        sorted_indices = sorted(range(len(modify_times)),
                                key=lambda k: modify_times[k], reverse=True)
        shapefile = shapefiles[sorted_indices[0]]
    else:
        shapefile = shapefiles[0]
    if not silent:
        print(f"Reading a shapefile from {shapefile}")
    shape_file = gpd.read_file(shapefile)
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
