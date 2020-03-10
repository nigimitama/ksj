Examples
========

公開されているデータの一覧を取得する
-------------------------------------

国土数値情報APIでダウンロードできるファイルの概要一覧を取得するには、 ``ksj.get_summary()`` を使います。

.. code:: python

    import ksj
    ksj_summary = ksj.get_summary()
    ksj_summary.head()

.. code::

      identifier      title    field1 field2 areaType
    0        A03  三大都市圏計画区域      政策区域   大都市圏        2
    1        A09       都市地域  国土（水・土地）   土地利用        3
    2        A10     自然公園地域        地域   保護保全        3
    3        A11     自然保全地域        地域   保護保全        3
    4        A12       農業地域  国土（水・土地）   土地利用        3


シェープファイルのURLを取得する
-------------------------------

``ksj.get_url()`` でシェープファイルのURLの一覧を取得します。

.. code:: python

    import ksj
    urls = ksj.get_url(identifier="N03", pref_code='11-14', fiscal_year=2019)
    urls.head()

.. code::

      identifier title field  year areaType areaCode datum                                         zipFileUrl zipFileSize
    0        N03  行政区域  政策区域  2019        3       11     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...      3.54MB
    1        N03  行政区域  政策区域  2019        3       12     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...      6.17MB
    2        N03  行政区域  政策区域  2019        3       13     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...     12.20MB
    3        N03  行政区域  政策区域  2019        3       14     1  http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2...      5.22MB

指定できるパラメータの詳細については国土数値情報APIの `公式ドキュメント <http://nlftp.mlit.go.jp/ksj/api/specification_api_ksj.pdf>`_ （pdf）をご参照ください 。


シェープファイルを取得して読み込む
----------------------------------

``ksj.read_shp()`` でシェープファイルをダウンロードして読み込みます。

.. code:: python

    import ksj

    # URLを取得
    urls = ksj.get_url(identifier="N03", pref_code='13', fiscal_year=2019)
    url = urls["zipFileUrl"][0]

    # ファイルをダウンロードし、geopandasで読み込む
    shape_gdf = ksj.read_shp(url)
    shape_gdf.head()

.. code::

      N03_001 N03_002 N03_003 N03_004 N03_007                                           geometry
    0     東京都    None    None    千代田区   13101  POLYGON ((139.77287 35.70370, 139.77279 35.703...
    1     東京都    None    None     中央区   13102  POLYGON ((139.78341 35.69645, 139.78459 35.696...
    2     東京都    None    None      港区   13103  POLYGON ((139.77129 35.62841, 139.77128 35.628...
    3     東京都    None    None      港区   13103  POLYGON ((139.76689 35.62774, 139.76718 35.627...
    4     東京都    None    None      港区   13103  POLYGON ((139.77022 35.63199, 139.77046 35.631...


ファイルをダウンロードする
--------------------------

``ksj.get_shp()`` でシェープファイルが入ったzipファイルを指定した場所にダウンロードします。

.. code:: python

    import ksj

    # URLを取得
    urls = ksj.get_url(identifier="N03", pref_code='13', fiscal_year=2019)
    url = urls["zipFileUrl"][0]

    # ファイルのダウンロード
    ksj.get_shp(url, path="./")



列名を日本語に変換する
----------------------

取得したシェープファイルの列名は ``N03_001`` のようなコードになっています。
これらのコードを日本語の列名へと変換したい場合は ``ksj.translate()`` が役に立つはずです。

.. code:: python

    import ksj

    # URLを取得
    urls = ksj.get_url(identifier="N03", pref_code='13', fiscal_year=2019)
    url = urls["zipFileUrl"][0]

    # ファイルをダウンロードし、geopandasで読み込む
    shape_gdf = ksj.read_shp(url)

    # 列名を日本語に変換
    shape_gdf = ksj.translate(shape_gdf)
    shape_gdf.head()

.. code::

      都道府県名   支庁名 郡政令都市 市区町村名 行政区域コード                                           geometry
    0   東京都  None  None  千代田区   13101  POLYGON ((139.77287 35.70370, 139.77279 35.703...
    1   東京都  None  None   中央区   13102  POLYGON ((139.78341 35.69645, 139.78459 35.696...
    2   東京都  None  None    港区   13103  POLYGON ((139.77129 35.62841, 139.77128 35.628...
    3   東京都  None  None    港区   13103  POLYGON ((139.76689 35.62774, 139.76718 35.627...
    4   東京都  None  None    港区   13103  POLYGON ((139.77022 35.63199, 139.77046 35.631...


.. note::

    年度によって列名コードの意味が変化する列（全体の１割程度）についてはまだ対応できておりません。その場合は変換されず、元の列名のままになります。
