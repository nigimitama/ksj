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


def read_shp(file_url, save_dir=None, save_file_name=None,
             return_type='auto', verbose=1):
    """
    指定したURLのzipファイルを指定フォルダあるいは一時フォルダにダウンロードし、
    解凍してgeopandasで開く。複数ある場合はリストで返す。

    Parameters
    ----------
    file_url : str
        国土数値情報ダウンロードサービスが提供するzipファイルのURL
    save_dir : str
        保存先ディレクトリのパス
    save_file_name : str
        保存するzipファイルの名前（任意）
    return_type : str
        返り値の型を指定します。（default = "auto"）
        "auto"の場合、zipファイル内のシェープファイルが1つならGeoDataFrame、複数ならGeoDataFrameのlistで返します。
        "list"の場合、常にGeoDataFrameのリストを返します。
    verbose : int
        メソッドの動作の様子を表示する度合いを指定します。
        0の場合、一切の表示を無効にします。
        1の場合、読み込み失敗など例外的な状況になった場合のみ表示を行います。
        2の場合、ファイルをどこに解凍したかについての表示を行います。

    Returns
    -------
    geopandas.GeoDataFrame or list
        読み込んだシェープファイルのデータ。
        一つのzipファイルに複数のシェープファイルがある場合、GeoDataFrameをリストに入れて返します。
    """
    if (return_type != "auto") and (return_type != "list"):
        raise NameError("'return_type' must be 'auto' or 'list'")
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
    file_pathes = _get_files(extract_dir)
    shapefiles = [f for f in file_pathes if ".shp" in f]
    if len(shapefiles) == 0:
        if verbose >= 1:
            print("shapefile not found")
    else:
        shape_files = [_read_geofile(shp, verbose) for shp in shapefiles]
        if (len(shape_files) == 0) and (return_type != "list"):
            shape_files = shape_files[0]
        else:
            if verbose >= 1:
                print("multiple shapefiles found, return as list")
    if save_dir is None:
        temp_dir.cleanup()
    return shape_files


def _read_geofile(file_path: str, verbose=1) -> gpd.GeoDataFrame:
    """
    geopandasで開ける地理データを読み込む
    既知の破損により読み込めないshpファイルは、同名のgeojsonがある場合そちらを読み込む
    """
    try:
        if verbose >= 2:
            print(f"reading a shapefile from {file_path}")
        gdf = gpd.read_file(file_path)
    except AttributeError:
        # A16-15_00_DID.shpはAttributeErrorで開けないが、同名のgeojsonは開ける
        # shpファイルと同名のgeojsonが同梱されているzipが124個ある
        if verbose >= 1:
            print(f"cannot read {file_path}")
        same_name_geojson = file_path.replace(".shp", ".geojson")
        if os.path.exists(same_name_geojson):
            if verbose >= 1:
                print(f"{same_name_geojson} found, trying to read it...")
            gdf = gpd.read_file(same_name_geojson)
            if verbose >= 1:
                print(f"done!")
        else:
            gdf = None
    return gdf


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
