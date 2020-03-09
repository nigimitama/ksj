# ksj: Kokudo Suuchi Jouhou API Client

[![CircleCI](https://circleci.com/gh/nigimitama/ksj/tree/master.svg?style=svg)](https://circleci.com/gh/nigimitama/ksj/tree/master)

[国土数値情報ダウンロードサービス](http://nlftp.mlit.go.jp/ksj/index.html)のWeb APIを簡単に使うためのPythonパッケージです。

データ分析での利用を想定しており、本パッケージのメソッドの返り値はpandasやgeopandasのオブジェクトになります。



## インストール

### 必要環境

- Python 3.6以上



### 依存パッケージ

本パッケージは以下のパッケージを使用します。

    lxml>=4.4.0
    xmljson>=0.2.0
    xlrd>=1.2.0
    geopandas>=0.6.0



### インストール方法

⚠️Windowsの場合[geopandasの依存パッケージ](http://geopandas.org/install.html#installing-with-pip)がpipではインストールできないため、**先にそちらをインストールする必要があります。** ご注意ください。

UNIX系OSの場合、`pip install ksj`だけでgeopandasもインストールされます。

```
pip install ksj
```



## 使用方法

※ [ドキュメント](https://nigimitama.github.io/ksj/)もあります。



### 読み込み

```python
import ksj
```



### 公開データの一覧を取得する

```python
# 国土数値情報APIでダウンロードできるファイルの概要一覧を取得（return: pd.DataFrame）
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

指定できるパラメータの詳細については国土数値情報APIの[公式ドキュメント](http://nlftp.mlit.go.jp/ksj/api/specification_api_ksj.pdf)（pdf）をご参照ください 。

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



### シェープファイルが入ったzipファイルをダウンロード

国土数値情報ダウンロードサービスからシェープファイルが入ったzipファイルをダウンロードします。

```python
# シェープファイルが入ったzipファイルのダウンロード
url = urls["zipFileUrl"][0]
ksj.get_shp(url, path="./shapefile")
```



### シェープファイルをダウンロードして読み込む

```python
# ファイルをダウンロードし、解凍してgeopandasで読み込む
shape_gdf = ksj.read_shp(url)
shape_gdf.head()
```


|      | N03_001 | N03_002 |    N03_003 | N03_004 | N03_007 |                                          geometry |
| ---: | ------: | ------: | ---------: | ------: | ------: | ------------------------------------------------: |
|    0 |  埼玉県 |    None | さいたま市 |    西区 |   11101 | POLYGON ((139.54776 35.93420, 139.54720 35.934... |
|    1 |  埼玉県 |    None | さいたま市 |    西区 |   11101 | POLYGON ((139.54776 35.93420, 139.54804 35.934... |
|    2 |  埼玉県 |    None | さいたま市 |    北区 |   11102 | POLYGON ((139.61753 35.96486, 139.61798 35.964... |
|    3 |  埼玉県 |    None | さいたま市 |  大宮区 |   11103 | POLYGON ((139.63768 35.92278, 139.63804 35.922... |
|    4 |  埼玉県 |    None | さいたま市 |  見沼区 |   11104 | POLYGON ((139.66718 35.96444, 139.66739 35.964... |



### 列名を日本語に変換する

列名を`N03_001`のようなコードから日本語の列名へと変換します。

年度によって列名の意味が変化する列（全体の１割程度）についてはまだ対応できておりません。その場合は変換されず、元の列名のままになります。

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



## 利用上の注意

APIの利用やAPIで得られる国土数値情報の利用にあたっては、国土数値情報ダウンロードサービスの利用約款および同Web APIの利用規約をご確認の上ご利用ください。

- http://nlftp.mlit.go.jp/ksj/other/yakkan.html
- http://nlftp.mlit.go.jp/ksj/api/about_api.html


