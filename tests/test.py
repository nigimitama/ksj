import unittest
import sys
import os
sys.path.append(os.path.abspath("."))
import ksj
print(f"ksj version: {ksj.__version__}")
print("path:", ksj)


class TestGetSummary(unittest.TestCase):
    """test of get_summary()"""

    def test_get_summary(self):
        """正常系"""
        urls = ksj.get_summary()
        actual = urls.shape
        expected = (114, 5)
        self.assertEqual(expected, actual)


class TestGetUrl(unittest.TestCase):
    """tests of get_url()"""

    def test_multi_pref_code(self):
        """正常系"""
        urls = ksj.get_url(
            identifier="L01", pref_code='11-14', fiscal_year=2019)
        actual = urls.shape
        expected = (4, 9)
        self.assertEqual(expected, actual)

    def test_multi_year(self):
        """正常系"""
        urls = ksj.get_url(identifier="L01", pref_code='11,12',
                           fiscal_year='2018,2019')
        actual = urls.shape
        expected = (4, 9)
        self.assertEqual(expected, actual)

    def test_multi_year_with_space(self):
        """準正常系: invalid input"""
        urls = ksj.get_url(identifier="L01", pref_code='11, 12',
                           fiscal_year='2018, 2019')
        actual = urls
        expected = None
        self.assertEqual(expected, actual)

    def test_mesh_code(self):
        """正常系"""
        urls = ksj.get_url(identifier="A30a5",
                           mesh_code=5340, fiscal_year=2011)
        expected = (1, 9)
        actual = urls.shape
        self.assertEqual(expected, actual)

    def test_future_year(self):
        """準正常系: invalid input"""
        urls = ksj.get_url(
            identifier="L01", pref_code='11-14', fiscal_year=2030)
        actual = urls
        expected = None
        self.assertEqual(expected, actual)


class TestGetShp(unittest.TestCase):

    def test_to_dir(self):
        """正常系"""
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        save_dir = "/tmp/testing"
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        ksj.get_shp(url, path=save_dir)
        has_zip = os.path.basename(url) in os.listdir(save_dir)
        self.assertTrue(has_zip)

    def test_as_file(self):
        """正常系"""
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        save_dir = "/tmp/testing.zip"
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        ksj.get_shp(url, path=save_dir)
        has_zip = os.path.basename(url) in os.listdir(save_dir)
        self.assertTrue(has_zip)


class TestReadShp(unittest.TestCase):

    # TODO: 複数のshpが入ったzipの場合
    def test_n03(self):
        """正常系"""
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        gdf = ksj.read_shp(url)
        actual = gdf.shape
        expected = (1525, 6)
        self.assertEqual(expected, actual)

    def test_n03_list(self):
        """正常系"""
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        gdf = ksj.read_shp(url, return_type="list")
        actual = type(gdf)
        expected = list
        self.assertEqual(expected, actual)

    def test_a30(self):
        """正常系"""
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/A30a5/A30a5-11/A30a5-11_5340-jgd_GML.zip'
        gdf = ksj.read_shp(url)
        actual = gdf.shape
        expected = (10, 11)
        self.assertEqual(expected, actual)

    def test_a16(self):
        """正常系、shapefileが破損していてgeojsonしか読めないもの"""
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/A16/A16-15/A16-15_01_GML.zip'
        gdf = ksj.read_shp(url)
        actual = gdf.shape
        expected = (119, 12)
        self.assertEqual(expected, actual)


class TestTranslate(unittest.TestCase):
    """tests of translate()"""

    def test_n03(self):
        """正常系"""
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_13_GML.zip'
        gdf = ksj.read_shp(url)
        actual = ksj.translate(gdf).columns.tolist()
        expected = ['都道府県名', '支庁名', '郡政令都市', '市区町村名', '行政区域コード', 'geometry']
        self.assertEqual(expected, actual)

    # def test_n06(self):
    #     """正常系"""
    #     # TODO:ローカルだとうまくいくのにCircleCIだと落ちる謎を解く
    #     url = 'http://nlftp.mlit.go.jp/ksj/gml/data/N06/N06-13/N06-13.zip'
    #     gdf = ksj.read_shp(url)[1]
    #     actual = ksj.translate(gdf).columns.tolist()
    #     expected = ['供用開始年', '設置期間(開始年)', '設置期間(終了年)', '関係ID',
    #                 '変遷ID', '変遷備考', '地点名', '接合部種別', 'geometry']
    #     self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
