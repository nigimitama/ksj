import ksj

# 国土数値情報APIでダウンロードできるファイル概要（return: pd.DataFrame）
ksj_summary = ksj.get_summary()
print(ksj_summary.head())

# 国土数値情報のzipファイルのURLを取得（return: pd.DataFrame）
identifier = "N03"
urls = ksj.get_url(identifier=identifier, pref_code='11-14', fiscal_year=2019)
print(urls.head())

# shpファイルが入ったzipファイルのダウンロードと解凍
url = urls["zipFileUrl"][0]
print(ksj.get_shp(url, save_dir="./shapefile", silent=False))

# ファイルを指定フォルダあるいは一時フォルダにダウンロードし、解凍してgeopandasで読み込む
url = urls["zipFileUrl"][0]
shape_gdf = ksj.read_shp(url, silent=False)
print(shape_gdf.head())

# 簡単に自動変換できる列名（年度によって意味が変わることのない列）に限り、列名を日本語に変換
shape_gdf = ksj.translate(shape_gdf)
print(shape_gdf.head())

# 列名の対応表をダウンロードして結合して開く（return: pd.DataFrame）
book = ksj.get_column_table()
print(book.head())
print(book.query(f"識別子 == '{identifier}'"))
