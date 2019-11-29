import ksj
import pandas as pd

column_data = ksj.get_column_table()\
    .rename(columns={"識別子": "identifier", "データ項目": "item",
                     "タグ名": "tag", "対応番号": "code", 
                     "属性名": "name", "": "note"})

has_year = column_data["item"].str.contains("年")
column_data.loc[has_year, :].to_csv("column_data/has_year.csv", index=False)
column_data.loc[~has_year, :].to_csv("column_data/hasnt_year.csv", index=False)
