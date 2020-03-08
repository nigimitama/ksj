import pandas as pd
from lxml import etree
import xmljson
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError


def get_summary() -> pd.DataFrame:
    """国土数値情報の概要情報（取得できるデータ一覧）を取得する

    Returns
    -------
    pandas.DataFrame
        国土数値情報APIで取得できるデータの一覧
    
    Example
    -------
    >>> import ksj
    >>> ksj_summary = ksj.get_summary()
    >>> ksj_summary.head()
      identifier      title    field1 field2 areaType
    0        A03  三大都市圏計画区域      政策区域   大都市圏        2
    1        A09       都市地域  国土（水・土地）   土地利用        3
    2        A10     自然公園地域        地域   保護保全        3
    3        A11     自然保全地域        地域   保護保全        3
    4        A12       農業地域  国土（水・土地）   土地利用        3
    """
    # const params（2020年現在この値以外を受け付けない）
    app_id = "ksjapibeta1"
    lang = "J"
    data_format = 1
    # set url and params
    api_url = "http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJSummary.xml"
    # NOTE: 仕様書では'dataFormat'なのだが、実際は'dataformat'に送らないとエラーになる
    params = {"appId": app_id, "lang": lang, "dataformat": data_format}
    # request
    response, error = _get_request(api_url, params=params)
    if error is not None:
        print(error)
        return None
    root = etree.fromstring(response)
    # convert xml to dict
    data_dict = xmljson.yahoo.data(root)
    # error
    error_msg = data_dict["KSJ_SUMMARY_INF"]["RESULT"]["ERROR_MSG"]
    if error_msg != "正常に終了しました。":
        print(error_msg)
    else:
        # convert dict to pd.DataFrame
        data_df = pd.json_normalize(
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
    
    Example
    -------
    >>> import ksj
    >>> urls = ksj.get_url(identifier="N03", pref_code='11-14', fiscal_year=2019)
    >>> urls.head()
      identifier title field  year areaType areaCode datum                                         zipFileUrl zipFileSize
    0        N03  行政区域  政策区域  2019        3       11     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...      3.54MB
    1        N03  行政区域  政策区域  2019        3       12     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...      6.17MB
    2        N03  行政区域  政策区域  2019        3       13     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...     12.20MB
    3        N03  行政区域  政策区域  2019        3       14     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...      5.22MB
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
    response, error = _get_request(api_url, params=params)
    if error is not None:
        print(error)
        return None
    # convert to xml
    root = etree.fromstring(response)
    # convert xml to dict
    data_dict = xmljson.yahoo.data(root)

    error_msg = data_dict["KSJ_URL_INF"]["RESULT"]["ERROR_MSG"]
    if error_msg != "正常に終了しました。":
        print(error_msg)
        return None
    else:
        # convert dict to pd.DataFrame
        data_df = pd.json_normalize(
            data_dict["KSJ_URL_INF"]["KSJ_URL"]["item"])
        return data_df


def _get_request(url: str, params: dict) -> list:
    """リクエストパラメータ付きでGETリクエストを送る"""
    url = url + "?" + urlencode(params)
    response, error = None, None
    try:
        req = Request(url)
        with urlopen(req) as res:
            response = res.read()
    except HTTPError as e:
        error = e
    except URLError as e:
        error = e
    return response, error
