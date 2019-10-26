import os
import tempfile
import zipfile
from urllib.request import urlretrieve
import geopandas as gpd
import re


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
    elif re.search("(.zip)$", save_file_name) is None:
        save_file_name += ".zip"
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


def read_shp(file_url, save_dir=None, save_file_name=None, verbose=1):
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
    verbose : int
        メソッドの動作の様子を表示する度合い。
        0の場合、一切の表示を無効にします。
        1の場合、読み込み失敗など例外的な状況になった場合のみ表示を行います。
        2の場合、ファイルをどこに解凍したかについての表示を行います。

    Returns
    -------
    geopandas.GeoDataFrame or list
        シェープファイルのデータ（複数ある場合はリストで返す）
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
    if verbose >= 2:
        print(f"{save_file_name} is extracted to {extract_dir}")
    # load
    file_names = _get_files(extract_dir)
    shapefiles = [f for f in file_names if ".shp" in f]
    geojesons = [f for f in file_names if ".geojson" in f]
    if len(shapefiles) == 0:
        if verbose >= 1:
            print("shapefile not found")
    else:
        shape_files = []
        for shapefile in shapefiles:
            if verbose >= 2:
                print(f"reading a shapefile from {shapefile}")
            try:
                shape_file = gpd.read_file(shapefile)
            except AttributeError:  # A16-15_00_DID.shpはAttributeErrorで開けない
                if verbose >= 1:
                    print(f"cannot read {shapefile}")
                    shape_file = None
                if len(geojesons) > 0:
                    file_name = os.path.splitext(os.path.basename(shapefile))[0]
                    same_name_geojsons = [f for f in geojesons if file_name in f]
                    gdfs = []
                    for geojson in same_name_geojsons:
                        if verbose >= 1:
                            print(f"trying to read {geojson} ...")
                        gdfs.append(gpd.read_file(geojson))
                    shape_file = gdfs[0] if (len(gdfs) == 0) else gdfs
            shape_files.append(shape_file)
        shape_file = shape_files[0] if (len(shape_files) == 0) else shape_files
    if save_dir is None:
        temp_dir.cleanup()
    return shape_file


# def read_gdf(file_path: str, verbose: int) -> gpd.GeoDataFrame:
#     """
#     概要：まず.shpファイルを開こうとし、もしそれが失敗したらgeojsonを読み込む
#     背景：A16-15_00_DID.shpはAttributeErrorで開けないが、同名のgeojsonが入っていてそちらは開ける

#     file_path: shapefile path
#     """
#     try:
#         shapefile = gpd.read_file(file_path)
#     except AttributeError:
#         if verbose >= 1:
#             print(f"cannot read {file_path}")
#         file_name = os.path.splitext(os.path.basename(file_path))

#         if len(geojesons) > 0:
#             geojeson = geojesons[0]
#             if verbose >= 1:
#                 print(f"trying to read {geojeson} ...")
#             gdfs = [gpd.read_file(f) for f in geojesons]
#             shape_file = gdfs[0] if (len(gdfs) == 0) else gdfs

#     return shapefile


# def _print_if(condition, text):
#     """if文＋print文を1行で書くための関数"""
#     if condition:
#         print(text)

def _get_files(path: str) -> list:
    """get file pathes recursively"""
    file_names = []
    for (root, _, files) in os.walk(path):
        for f in files:
            file_names.append(os.path.join(root, f))
    return file_names
