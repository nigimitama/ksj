import os
import tempfile
import zipfile
from urllib.request import urlretrieve
import geopandas as gpd
import re


def read_shp(url, save_dir=None, save_name=None,
             return_type='auto', verbose=1):
    """指定したURLのシェープファイルを取得して読み込む。
    
    指定したURLのzipファイルを一時フォルダにダウンロードし、解凍してGeoDataFrameで開く。
    稀に一つのzipファイルに複数のシェープファイルが含まれるものもあるが、その場合はGeoDataFrameのリストで返す。

    Parameters
    ----------
    url : str
        国土数値情報ダウンロードサービスが提供するzipファイルのURL
    return_type : str
        返り値の型を指定します。（default = "auto"）
        "auto"の場合、zipファイル内のシェープファイルが1つならGeoDataFrame、複数ならGeoDataFrameのlistで返します。
        "list"の場合、常にGeoDataFrameのlistを返します。
    verbose : int
        メソッドの動作の様子を表示する度合いを指定します。
        0の場合、一切の表示を無効にします。
        1の場合、読み込み失敗など例外的な状況になった場合のみ表示を行います。
        2の場合、ファイルをどこに解凍したかについての表示を行います。

    Returns
    -------
    geopandas.GeoDataFrame or list
        読み込んだシェープファイルのデータ。
        一つのzipファイルに複数のシェープファイルがある場合、GeoDataFrameをlistに入れて返します。
    
    Example
    -------
    >>> import ksj
    >>> urls = ksj.get_url(identifier='N03', pref_code='13', fiscal_year=2019)
    >>> url = urls['zipFileUrl'][0]
    >>> shape_gdf = ksj.read_shp(url)
    >>> shape_gdf.head()
      N03_001 N03_002 N03_003 N03_004 N03_007                                           geometry
    0     東京都    None    None    千代田区   13101  POLYGON ((139.77287 35.70370, 139.77279 35.703...
    1     東京都    None    None     中央区   13102  POLYGON ((139.78341 35.69645, 139.78459 35.696...
    2     東京都    None    None      港区   13103  POLYGON ((139.77129 35.62841, 139.77128 35.628...
    3     東京都    None    None      港区   13103  POLYGON ((139.76689 35.62774, 139.76718 35.627...
    4     東京都    None    None      港区   13103  POLYGON ((139.77022 35.63199, 139.77046 35.631...
    """
    if (return_type != "auto") and (return_type != "list"):
        raise NameError("'return_type' must be 'auto' or 'list'")
    # make temporaty directory
    save_name = os.path.basename(url)
    temp_dir = tempfile.TemporaryDirectory()
    save_dir = temp_dir.name
    save_path = os.path.join(save_dir, save_name)
    # download
    urlretrieve(url=url, filename=save_path)
    # unzip
    name_without_extension = os.path.splitext(save_name)[0]
    extract_dir = os.path.join(save_dir, name_without_extension)
    if not os.path.exists(extract_dir):
        os.mkdir(extract_dir)
    with zipfile.ZipFile(save_path) as existing_zip:
        # 文字化け回避のため変換処理を逐次挟む
        for info in existing_zip.infolist():
            info.filename = info.filename.encode('cp437').decode('cp932')
            existing_zip.extract(info, path=extract_dir)
    if verbose >= 2:
        print(f"{save_name} was extracted to {extract_dir}")
    # load
    file_paths = _get_files(extract_dir)
    shapefiles = [f for f in file_paths if f.endswith(".shp")]
    if len(shapefiles) == 0:
        if verbose >= 1:
            print("shapefile not found")
    else:
        shape_files = [_read_geofile(shp, verbose) for shp in shapefiles]
        if (len(shape_files) >= 2) and (verbose >= 1):
            print("multiple shapefiles are found, return as list")
        if (len(shape_files) == 1) and (return_type != "list"):
            shape_files = shape_files[0]
    temp_dir.cleanup()
    return shape_files


def get_shp(url: str, save_dir: str, save_name=None,
            unzip=False, verbose=1) -> None:
    """指定したURLのzipファイルを指定フォルダにダウンロードする。

    Parameters
    ----------
    url : str
        国土数値情報ダウンロードサービスが提供するzipファイルのURL
    save_dir : str
        保存先ディレクトリのパス
    save_name : str
        保存するzipファイルの名前
    unzip : bool
        Trueの場合、zipファイルの解凍まで行います。
    verbose : int
        メソッドの動作の様子を表示する度合いを指定します。
        0の場合、一切の表示を無効にします。
        1の場合、ファイルをどこに解凍したかについての表示を行います。
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if save_name is None:
        save_name = os.path.basename(url)
    elif re.search("(.zip)$", save_name) is None:
        save_name += ".zip"
    save_path = os.path.join(save_dir, save_name)
    urlretrieve(url=url, filename=save_path)
    if verbose > 0:
        print(f"{save_name} was saved at {save_dir}")
    if unzip:
        name_without_extension = os.path.splitext(save_name)[0]
        extract_dir = os.path.join(save_dir, name_without_extension)
        if not os.path.exists(extract_dir):
            os.mkdir(extract_dir)
        with zipfile.ZipFile(save_path) as existing_zip:
            # 文字化け回避のため変換処理を逐次挟む
            for info in existing_zip.infolist():
                info.filename = info.filename.encode('cp437').decode('cp932')
                existing_zip.extract(info, path=extract_dir)
        if verbose > 0:
            print(f"{save_name} was extracted to {extract_dir}")


def _read_geofile(file_path: str, verbose=1) -> gpd.GeoDataFrame:
    """
    geopandasで開ける地理データを読み込む
    既知の破損により読み込めないshpファイルは、同名のgeojsonがある場合そちらを読み込む
    """
    try:
        if verbose >= 2:
            print(f"reading a shapefile from {file_path}")
        gdf = gpd.read_file(file_path, encoding="CP932")
    except AttributeError:
        # A16-15_00_DID.shpはAttributeErrorで開けないが、同名のgeojsonは開ける
        # shpファイルと同名のgeojsonが同梱されているzipが124個ある
        if verbose >= 1:
            print(f"cannot read {file_path}")
        same_name_geojson = file_path.replace(".shp", ".geojson")
        if os.path.exists(same_name_geojson):
            if verbose >= 1:
                print(f"{same_name_geojson} found, trying to read it...")
            gdf = gpd.read_file(same_name_geojson, encoding="CP932")
            if verbose >= 1:
                print(f"finished.")
        else:
            gdf = None
    return gdf


def _get_files(path: str) -> list:
    """get file paths recursively"""
    file_names = []
    for (root, _, files) in os.walk(path):
        for f in files:
            file_names.append(os.path.join(root, f))
    return file_names
