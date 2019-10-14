import os
import tempfile
import xlrd
import zipfile
from urllib.request import urlretrieve
import pandas as pd
import requests
from lxml import etree
import xmljson
import geopandas as gpd
import json

def get_summary() -> pd.DataFrame:
    """
    国土数値情報の概要情報（取得できるデータ一覧）を取得する
    """
    # const params
    app_id = "ksjapibeta1"
    lang = "J"
    data_format = 1
    # set url and params
    api_url = "http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJSummary.xml"
    # 仕様書では'dataFormat'なのだが、実際は'dataformat'に送らないとエラーになる
    params = {"appId": app_id, "lang": lang, "dataformat": data_format}
    # request
    response = requests.get(api_url, params=params)
    root = etree.fromstring(response.content)
    # convert xml to dict
    data_dict = xmljson.yahoo.data(root)
    # error
    error_msg = data_dict["KSJ_SUMMARY_INF"]["RESULT"]["ERROR_MSG"]
    if error_msg != "正常に終了しました。":
        print(error_msg)
    else:
        # convert dict to pd.DataFrame
        data_df = pd.io.json.json_normalize(
            data_dict["KSJ_SUMMARY_INF"]["KSJ_SUMMARY"]["item"])
    return data_df


def get_url(identifier, pref_code=None, mesh_code=None, metro_area=None, fiscal_year=None):
    """
    国土数値情報のURLを取得する
    """
    # const params
    app_id = "ksjapibeta1"
    lang = "J"
    data_format = 1
    # set url and params
    api_url = "http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJURL.xml"
    params = {"appId": app_id, "lang": lang,
              "dataformat": data_format, "identifier": identifier}
    if pref_code:
        params["prefCode"] = pref_code
    if mesh_code:
        params["meshCode"] = mesh_code
    if metro_area:
        params["metroArea"] = metro_area
    if fiscal_year:
        params["fiscalyear"] = fiscal_year
    # request
    response = requests.get(api_url, params=params)
    # convert to xml
    root = etree.fromstring(response.content)
    # convert xml to dict
    data_dict = xmljson.yahoo.data(root)

    error_msg = data_dict["KSJ_URL_INF"]["RESULT"]["ERROR_MSG"]
    if error_msg != "正常に終了しました。":
        print(error_msg)
    else:
        # convert dict to pd.DataFrame
        data_df = pd.io.json.json_normalize(
            data_dict["KSJ_URL_INF"]["KSJ_URL"]["item"])
    return data_df


def download_and_unzip(file_url, save_dir, save_file_name=None, silent=None):
    """
    指定したURLのzipファイルを指定フォルダにダウンロードし、解凍する
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    save_file_name = os.path.basename(
        file_url) if save_file_name is None else save_file_name
    save_path = os.path.join(save_dir, save_file_name)
    urlretrieve(url=file_url, filename=save_path)
    # extract to save_dir
    with zipfile.ZipFile(save_path) as existing_zip:
        existing_zip.extractall(save_dir)
    if not silent:
        print(f"{save_file_name} is extracted to {save_dir}")


def download_and_load(file_url, save_dir=None, save_file_name=None, silent=None):
    """
    指定したURLのzipファイルを指定フォルダあるいは一時フォルダにダウンロードし、
    解凍してgeopandasで開く
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
    file_names = get_files(save_dir)
    shapefiles = [file_name for file_name in file_names if ".shp" in file_name]
    modify_times = [os.lstat(shapefile).st_mtime for shapefile in shapefiles]
    sorted_indices = sorted(range(len(modify_times)),
                            key=lambda k: modify_times[k], reverse=True)
    newest_mod_file = shapefiles[sorted_indices[0]]
    file_path = os.path.join(save_dir, newest_mod_file)
    print(f"Loading {file_path}")
    return gpd.read_file(file_path)


def get_files(path: str) -> list:
    """get file pathes recursively"""
    file_names = []
    for (root, dirs, files) in os.walk(path):
        for f in files:
            file_names.append(os.path.join(root, f))
    return file_names


def get_shape_property_table(silent=True) -> xlrd.book.Book:
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
    return xlrd.open_workbook(file_path)


def get_column_table(silent=True) -> pd.DataFrame:
    """
    列名の対応表xlsファイルを開き、全シートを結合して単一のデータフレームにして返す。
    """
    book = get_shape_property_table(silent=silent)
    sheets = []
    for sheet_name in book.sheet_names():
        sheet = get_sheet(book=book, sheet_name=sheet_name)
        sheets.append(sheet)
    return pd.concat(sheets, axis=0, sort=False)


def get_sheet(book: xlrd.book.Book, sheet_name=False) -> pd.DataFrame:
    """
    指定したsheet nameのシートをpandasで開く
    """
    sheet = book.sheet_by_name(sheet_name)
    table = [sheet.row_values(row) for row in range(sheet.nrows)]
    index = get_content_start_row_index(table)
    return pd.DataFrame(table[index+1:], columns=table[index])


def get_content_start_row_index(table: list) -> int:
    """
    表頭っぽい行にきたらbreakして行番号を取得する
    """
    for i in range(len(table)):
        if ("属性名" in table[i]) or ("データ項目" in table[i]):
            break
    return i


def translate(data: pd.DataFrame) -> pd.DataFrame:
    """自動変換できる列（年度によって意味が変わらない列）に限り、列名を変換する"""
    with open("./data/rename_dict.json", "r") as f:
        rename_dict = json.load(f)
    return data.rename(columns=rename_dict)
