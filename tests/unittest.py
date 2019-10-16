import unittest
from ksj import kokudo_suuchi_jouhou as ksj


class TestGetSummary(unittest.TestCase):
    """test of get_summary()"""

    def test_get_summary(self):
        # 正常な入力
        urls = ksj.get_summary()
        actual = urls.shape
        expected = (114, 5)
        self.assertEqual(expected, actual)


class TestGetUrl(unittest.TestCase):
    """tests of get_url()"""

    def test_multi_pref_code(self):
        # 正常な入力
        urls = ksj.get_url(
            identifier="L01", pref_code='11-14', fiscal_year=2019)
        actual = urls.shape
        expected = (4, 9)
        self.assertEqual(expected, actual)

    def test_multi_year(self):
        # 正常な入力
        urls = ksj.get_url(identifier="L01", pref_code='11,12',
                           fiscal_year='2018,2019')
        actual = urls.shape
        expected = (4, 9)
        self.assertEqual(expected, actual)

    def test_mesh_code(self):
        # 正常な入力
        urls = ksj.get_url(identifier="A30a5",
                           mesh_code=5340, fiscal_year=2011)
        expected = (1, 9)
        actual = urls.shape
        self.assertEqual(expected, actual)

    def test_future_year(self):
        # 異常な入力
        urls = ksj.get_url(
            identifier="L01", pref_code='11-14', fiscal_year=2030)
        actual = urls
        expected = None
        self.assertEqual(expected, actual)


class TestReadShp(unittest.TestCase):

    def test_read_shp(self):
        # 正常な入力
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        gdf = ksj.read_shp(url)
        actual = gdf.shape
        expected = (1525, 6)
        self.assertEqual(expected, actual)

        # 正常な入力
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/A30a5/A30a5-11/A30a5-11_5340-jgd_GML.zip'
        gdf = ksj.read_shp(url)
        actual = gdf.shape
        expected = (10, 11)
        self.assertEqual(expected, actual)


class TestTranslate(unittest.TestCase):
    """tests of translate()"""

    def test_n03(self):
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_13_GML.zip'
        gdf = ksj.read_shp(url)
        actual = ksj.translate(gdf).columns.tolist()
        expected = ['都道府県名', '支庁名', '郡政令都市', '市区町村名', '行政区域コード', 'geometry']
        self.assertEqual(expected, actual)

    def test_n06(self):
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/N06/N06-13/N06-13.zip'
        gdf = ksj.read_shp(url)
        actual = ksj.translate(gdf).columns.tolist()
        expected = ['供用開始年', '設置期間(開始年)', '設置期間(終了年)', '関係ID',
                    '変遷ID', '変遷備考', '地点名', '接合部種別', 'geometry']
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
