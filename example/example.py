import kokudo_suuchi as ksj

# 国土数値情報APIでダウンロードできるファイル概要（pd.DataFrame）
ksj.get_summary()

# 国土数値情報のzipファイルのURLを取得（pd.DataFrame）
identifier = "N03"
urls = ksj.get_url(identifier=identifier, pref_code='11-14', fiscal_year=2019)
urls.head()

# zipファイルのダウンロードと解凍
url = urls["zipFileUrl"][0]
ksj.download_and_unzip(url, save_path="./example/shapefile/")

# 列名の対応表をダウンロードして結合して開く（pd.DataFrame）
book = ksj.get_column_table()
book.query(f"識別子 == '{identifier}'")

