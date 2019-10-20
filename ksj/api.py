import pandas as pd
import requests
from lxml import etree
import xmljson


def get_summary() -> pd.DataFrame:
    """国土数値情報の概要情報（取得できるデータ一覧）を取得する

    Returns
    -------
    pandas.DataFrame
        国土数値情報APIで取得できるデータの一覧
    """
    # const params（2019年現在この値以外を受け付けない）
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


def get_url(identifier: str, pref_code=None, mesh_code=None,
            metro_area=None, fiscal_year=None) -> pd.DataFrame:
    """国土数値情報のURL情報を取得する

    Parameters
    ----------
    identifier : str
        ファイルの識別子（例：「地価公示」なら'L01'）
    pref_code : str, int
        都道府県コード（例：13, '11,12', '11-14'）
    mesh_code : str, int
        メッシュコード。areaType=4の場合のみ有効。（例：5340）
    metro_area : str, int
        都市圏コード。areaType=2の場合のみ有効。（例：100）
    fiscal_year : str, int
        年度。（例：2017, '2015,2019', '2014-2016'）
    
    Returns
    -------
    pandas.DataFrame
        データの情報とzipファイルのURLが入ったデータフレーム
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
    if response.status_code != 200:
        print(f"Error! status code {response.status_code}")
        return None
    # convert to xml
    root = etree.fromstring(response.content)
    # convert xml to dict
    data_dict = xmljson.yahoo.data(root)

    error_msg = data_dict["KSJ_URL_INF"]["RESULT"]["ERROR_MSG"]
    if error_msg != "正常に終了しました。":
        print(error_msg)
        return None
    else:
        # convert dict to pd.DataFrame
        data_df = pd.io.json.json_normalize(
            data_dict["KSJ_URL_INF"]["KSJ_URL"]["item"])
        return data_df