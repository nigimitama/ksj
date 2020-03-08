import os
import tempfile
import xlrd
from urllib.request import urlretrieve
import pandas as pd
import geopandas as gpd


def get_column_table(silent=True) -> pd.DataFrame:
    """シェープファイルの列名の対応表を取得する。

    `シェープファイルの列名の対応表xls <http://nlftp.mlit.go.jp/ksj/gml/shape_property_table.xls>`__ を開き、ブック内の全シートを結合して単一のデータフレームにして返す。
    
    Returns
    -------
    pandas.DataFrame
        xlsファイル

    Example
    -------
    >>> import ksj
    >>> columns = ksj.get_column_table()
    >>> columns.head()
         識別子       データ項目                         タグ名      対応番号        属性名
    0  A02-a  指定地域3次メッシュ  DesignatedAreaTertiaryMesh  A02a_001  3次メッシュコード  NaN
    1  A02-a  指定地域3次メッシュ  DesignatedAreaTertiaryMesh  A02a_002   3次メッシュ面積  NaN
    2  A02-a  指定地域3次メッシュ  DesignatedAreaTertiaryMesh  A02a_003    農業地域の面積  NaN
    3  A02-a  指定地域3次メッシュ  DesignatedAreaTertiaryMesh  A02a_004    森林地域の面積  NaN
    4  A02-a  指定地域3次メッシュ  DesignatedAreaTertiaryMesh  A02a_005   都市計画区域面積  NaN
    """
    book = _get_shape_property_table(silent=silent)
    sheets = []
    for sheet_name in book.sheet_names():
        sheet = _get_sheet(book=book, sheet_name=sheet_name)
        sheets.append(sheet)
    return pd.concat(sheets, axis=0, sort=False)


def _get_shape_property_table(silent=True) -> xlrd.book.Book:
    """列名の対応表xlsファイルを一時フォルダにダウンロードし、開く。
    xlsファイルは開いてすぐ（メソッドの処理が終わるとともに）消去される
    """
    url = "http://nlftp.mlit.go.jp/ksj/gml/shape_property_table.xls"
    file_name = os.path.basename(url)
    temp_dir = tempfile.TemporaryDirectory()
    file_path = os.path.join(temp_dir.name, file_name)
    urlretrieve(url=url, filename=file_path)
    if not silent:
        print(f"shape_property_table is downloaded at {file_path}")
    book = xlrd.open_workbook(file_path)
    temp_dir.cleanup()
    return book


def _get_sheet(book: xlrd.book.Book, sheet_name=False) -> pd.DataFrame:
    """指定したsheet nameのシートをpandasで開く"""
    sheet = book.sheet_by_name(sheet_name)
    table = [sheet.row_values(row) for row in range(sheet.nrows)]
    index = _get_content_start_row_index(table)
    return pd.DataFrame(table[index+1:], columns=table[index])


def _get_content_start_row_index(table: list) -> int:
    """表頭っぽい行にきたらbreakして行番号を取得する"""
    for i in range(len(table)):
        if ("属性名" in table[i]) or ("データ項目" in table[i]):
            break
    return i


def translate(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """年度によって意味が変わらない列についてのみ列名を変換する。

    Parameters
    ----------
    data : geopandas.GeoDataFrame
        国土数値情報ダウンロードサービスから取得されたシェープファイル

    Returns
    -------
    geopandas.GeoDataFrame
        列名を日本語に変換したシェープファイル

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
    >>> shape_gdf = ksj.translate(shape_gdf)
    >>> shape_gdf.head()
      都道府県名   支庁名 郡政令都市 市区町村名 行政区域コード                                           geometry
    0   東京都  None  None  千代田区   13101  POLYGON ((139.77287 35.70370, 139.77279 35.703...
    1   東京都  None  None   中央区   13102  POLYGON ((139.78341 35.69645, 139.78459 35.696...
    2   東京都  None  None    港区   13103  POLYGON ((139.77129 35.62841, 139.77128 35.628...
    3   東京都  None  None    港区   13103  POLYGON ((139.76689 35.62774, 139.76718 35.627...
    4   東京都  None  None    港区   13103  POLYGON ((139.77022 35.63199, 139.77046 35.631...
    """
    # 列名の対応表をダウンロードして結合して開く
    book = get_column_table()
    # TODO: 2713列中2470列をこれで対応できるが、残り243列（年度によって意味が変わる列コード）は今後対応する
    unique_cols = book[["対応番号", "属性名"]].drop_duplicates()
    codes = list(unique_cols["対応番号"])
    names = list(unique_cols["属性名"])
    rename_dict = dict(zip(codes, names))
    # rename
    return data.rename(columns=rename_dict)
