import re

texts = ["平成30年以降"]
text = texts[0]
text = "昭和64年"





def wareki2seireki(wareki: str) -> int:
    """「平成8」「昭和53年」などを西暦(int)にする"""
    wareki_num = int(re.search(r"\d+", wareki).group())

    gengou_year = {
        "明治": 1868,
        "大正": 1912,
        "昭和": 1926,
        "平成": 1989,
        "令和": 2019
    }
    for gengou, base_year in gengou_year.items():
        if gengou in wareki:
            year = base_year + wareki_num - 1
    return year




wareki = re.search(r"(明治|大正|昭和|平成|令和)\d+年", text).group()

wareki2seireki(wareki)


def str2query(string: str, year: int) -> str:
    """
    「以前」「以降」をquery用の演算子にする
    `year <= wareki` の形を想定

    Parameters
    ----------
    string : str
        '平成25年～平成29年', '平成22年度', '平成29年度以降'など
    year : int
        queryで和暦と比較したい西暦（ksj dataのfiscal_year）
    """
    re.sub()

    data = {
        "以前": "<=",
        "以降": ">=",
        r"～|~": f"<= {year} <=",
        r"(明治|大正|昭和|平成|令和)\d+年": wareki2seireki(string),
    }

text = '平成25年～平成29年'
text = '平成29年度以降'
text = '道路密度・道路延長メッシュ(53, 14, 15, 16 昭和53年度, 平成14～16年度）'
wareki = re.search(r"(明治|大正|昭和|平成|令和).+年[度以前降]+", text).group()
wareki



import ksj
column_table = ksj.get_column_table()
drop_keyword = "年度作成データ"
has_year = column_table.query(f"データ項目.str.contains('年') and \
    not データ項目.str.contains('{drop_keyword}')")["データ項目"]\
        .drop_duplicates().values.tolist()



