# kokudo_suuchi

国土数値情報ダウンロードサービス Web APIの情報を取得するPythonライブラリです。

まだ製作中です。



## できること

- 国土数値情報ダウンロードサービスが提供するデータの概要を取得する

  ```python
  import kokudo_suuchi as ksj
  
  # 国土数値情報APIでダウンロードできるファイル概要（pd.DataFrame）
  ksj_summary = ksj.get_summary()
  ksj_summary.head()
  ```

  

- シェープファイルのURLを取得する

  ```python
  # 国土数値情報のzipファイルのURLを取得（pd.DataFrame）
  urls = ksj.get_url(identifier="N03", pref_code='11-14', fiscal_year=2019)
  urls.head()
  ```

  

- シェープファイルのzipファイルをダウンロードして解凍する

  ```python
  # zipファイルのダウンロードと解凍
  url = urls["zipFileUrl"][0]
  ksj.download_and_unzip(url, save_path="./shapefile/")
  ```

  

- 列名の対応表をダウンロードして開く

  ```python
  # 列名の対応表をダウンロードして結合して開く（pd.DataFrame）
  book = ksj.get_column_table()
  # 列名の対応表
  book.query("識別子 == 'N03'")
  ```

  

