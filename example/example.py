import kokudo_suuchi_jouhou as ksj

# 国土数値情報APIでダウンロードできるファイル概要（return: pd.DataFrame）
ksj_summary = ksj.get_summary()
ksj_summary.head()

# 国土数値情報のzipファイルのURLを取得（return: pd.DataFrame）
identifier = "N03"
urls = ksj.get_url(identifier=identifier, pref_code='11-14', fiscal_year=2019)
urls.head()

# zipファイルのダウンロードと解凍
url = urls["zipFileUrl"][0]
ksj.download_and_unzip(url, save_dir="./example/shapefile/", silent=False)

# ファイルを指定フォルダあるいは一時フォルダにダウンロードし、解凍してgeopandasで読み込む
url = urls["zipFileUrl"][0]
shape_gdf = ksj.download_and_load(url, silent=False)
shape_gdf.head()

# 簡単に自動変換できる列名（年度によって意味が変わらない列）に限り、列名を日本語に変換
shape_gdf = ksj.translate(shape_gdf)
shape_gdf.head()

# 列名の対応表をダウンロードして結合して開く（return: pd.DataFrame）
book = ksj.get_column_table()
book.head()
book.query(f"識別子 == '{identifier}'")
