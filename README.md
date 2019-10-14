# kokudo_suuchi_jouhou

国土数値情報ダウンロードサービス Web APIの情報を取得するPythonライブラリです。



## 使用法

### 国土数値情報ダウンロードサービスが提供するデータの概要を取得する

```python
import kokudo_suuchi_jouhou as ksj

# 国土数値情報APIでダウンロードできるファイル概要（pd.DataFrame）
ksj_summary = ksj.get_summary()
ksj_summary.head()
```

|      | identifier |              title |           field1 |   field2 | areaType |
| ---: | ---------: | -----------------: | ---------------: | -------: | -------: |
|    0 |        A03 | 三大都市圏計画区域 |         政策区域 | 大都市圏 |        2 |
|    1 |        A09 |           都市地域 | 国土（水・土地） | 土地利用 |        3 |
|    2 |        A10 |       自然公園地域 |             地域 | 保護保全 |        3 |
|    3 |        A11 |       自然保全地域 |             地域 | 保護保全 |        3 |
|    4 |        A12 |           農業地域 | 国土（水・土地） | 土地利用 |        3 |

### シェープファイルのURLを取得する

```python
# 国土数値情報のzipファイルのURLを取得（return: pd.DataFrame）
urls = ksj.get_url(identifier="N03", pref_code='11-14', fiscal_year=2019)
urls.head()
```

|      | identifier |    title |    field | year | areaType | areaCode | datum |                                        zipFileUrl | zipFileSize |
| ---: | ---------: | -------: | -------: | ---: | -------: | -------: | ----: | ------------------------------------------------: | ----------: |
|    0 |        N03 | 行政区域 | 政策区域 | 2019 |        3 |       11 |     1 | http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2... |      3.54MB |
|    1 |        N03 | 行政区域 | 政策区域 | 2019 |        3 |       12 |     1 | http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2... |      6.17MB |
|    2 |        N03 | 行政区域 | 政策区域 | 2019 |        3 |       13 |     1 | http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2... |     12.20MB |
|    3 |        N03 | 行政区域 | 政策区域 | 2019 |        3 |       14 |     1 | http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2... |      5.22MB |



### シェープファイルのzipファイルをダウンロードして解凍する

```python
# zipファイルのダウンロードと解凍
url = urls["zipFileUrl"][0]
ksj.download_and_unzip(url, save_path="./shapefile/")
```

```
N03-190101_11_GML.zip is extracted to ./example/shapefile/
```



### シェープファイルをダウンロードして読み込む

```python
# ファイルを指定フォルダあるいは一時フォルダにダウンロードし、解凍してgeopandasで読み込む
shape_gdf = ksj.download_and_load(url, silent=False)
shape_gdf.head()
```

```
N03-190101_11_GML.zip is extracted to /tmp/tmpd0s7e4oq
Loading /tmp/tmpd0s7e4oq/N03-19_11_190101.shp
```

|      | N03_001 | N03_002 |    N03_003 | N03_004 | N03_007 |                                          geometry |
| ---: | ------: | ------: | ---------: | ------: | ------: | ------------------------------------------------: |
|    0 |  埼玉県 |    None | さいたま市 |    西区 |   11101 | POLYGON ((139.54776 35.93420, 139.54720 35.934... |
|    1 |  埼玉県 |    None | さいたま市 |    西区 |   11101 | POLYGON ((139.54776 35.93420, 139.54804 35.934... |
|    2 |  埼玉県 |    None | さいたま市 |    北区 |   11102 | POLYGON ((139.61753 35.96486, 139.61798 35.964... |
|    3 |  埼玉県 |    None | さいたま市 |  大宮区 |   11103 | POLYGON ((139.63768 35.92278, 139.63804 35.922... |
|    4 |  埼玉県 |    None | さいたま市 |  見沼区 |   11104 | POLYGON ((139.66718 35.96444, 139.66739 35.964... |





### 列名の対応表をダウンロードして開く

- http://nlftp.mlit.go.jp/ksj/gml/shape_property_table.xls に列名の対応表の.xlsファイルが公開されているので、それを取得してpandasで読み込みます。

```python
# 列名の対応表をダウンロードして結合して開く（return: pd.DataFrame）
book = ksj.get_column_table()
book.head()
```

|      | 識別子 |          データ項目 |                     タグ名 | 対応番号 |            属性名 |      |
| ---: | -----: | ------------------: | -------------------------: | -------: | ----------------: | ---: |
|    0 |  A02-a | 指定地域3次メッシュ | DesignatedAreaTertiaryMesh | A02a_001 | 3次メッシュコード |  NaN |
|    1 |  A02-a | 指定地域3次メッシュ | DesignatedAreaTertiaryMesh | A02a_002 |   3次メッシュ面積 |  NaN |
|    2 |  A02-a | 指定地域3次メッシュ | DesignatedAreaTertiaryMesh | A02a_003 |    農業地域の面積 |  NaN |
|    3 |  A02-a | 指定地域3次メッシュ | DesignatedAreaTertiaryMesh | A02a_004 |    森林地域の面積 |  NaN |
|    4 |  A02-a | 指定地域3次メッシュ | DesignatedAreaTertiaryMesh | A02a_005 |  都市計画区域面積 |  NaN |



### 列名を日本語に変換

簡単に自動変換できる列名（年度によって意味が変わらない列）に限り、列名を日本語に変換します

```python
# 列名を日本語に変換
shape_gdf = ksj.translate(shape_gdf)
shape_gdf.head()
```

|      | 都道府県名 | 支庁名 | 郡政令都市 | 市区町村名 | 行政区域コード |                                          geometry |
| ---: | ---------: | -----: | ---------: | ---------: | -------------: | ------------------------------------------------: |
|    0 |     埼玉県 |   None | さいたま市 |       西区 |          11101 | POLYGON ((139.54776 35.93420, 139.54720 35.934... |
|    1 |     埼玉県 |   None | さいたま市 |       西区 |          11101 | POLYGON ((139.54776 35.93420, 139.54804 35.934... |
|    2 |     埼玉県 |   None | さいたま市 |       北区 |          11102 | POLYGON ((139.61753 35.96486, 139.61798 35.964... |
|    3 |     埼玉県 |   None | さいたま市 |     大宮区 |          11103 | POLYGON ((139.63768 35.92278, 139.63804 35.922... |
|    4 |     埼玉県 |   None | さいたま市 |     見沼区 |          11104 | POLYGON ((139.66718 35.96444, 139.66739 35.964... |