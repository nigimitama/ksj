import os
import tempfile
import xlrd
from urllib.request import urlretrieve
import pandas as pd
import geopandas as gpd


def get_column_table(silent=True) -> pd.DataFrame:
    """列名の対応表xlsファイルを開き、全シートを結合して単一のデータフレームにして返す。"""
    book = _get_shape_property_table(silent=silent)
    sheets = []
    for sheet_name in book.sheet_names():
        sheet = _get_sheet(book=book, sheet_name=sheet_name)
        sheets.append(sheet)
    return pd.concat(sheets, axis=0, sort=False)


def _get_shape_property_table(silent=True) -> xlrd.book.Book:
    """
    列名の対応表xlsファイルを一時フォルダにダウンロードし、開く。
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
