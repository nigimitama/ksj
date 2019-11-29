import re
import requests
import hashlib
import ksj
import time
from tqdm import tqdm
import pandas as pd
import os
import tempfile
import zipfile
import urllib
import geopandas as gpd
output_name = "gen_data/unique_urls_hashes_temp.csv"
ksj_data = pd.read_csv(output_name)

output_name = "gen_data/ksj_urls.csv"
urls = pd.read_csv(output_name)

"""
1. urlsからyearの最小最大値を取得
2. 列名変換表にyearを追加して、最小値から最大値までの文だけ水増し
3. join
"""

kt = ksj.get_column_table()\
    .rename(columns={"識別子": "identifier", "データ項目": "item", "タグ名": "tag",
                     "対応番号": "code", "属性名": "name", "": "note"})


text = ksj_data.query(
    "identifier == 'A03' and areaCode == 100")["columns"].values.item()

str2list(text)

def str2list(text: str) -> list:
    """リスト全体を文字列にした"['a', 'b']"のような文字列をリストにする"""
    return re.sub("[\[\]'\s]", "", text).split(",")


