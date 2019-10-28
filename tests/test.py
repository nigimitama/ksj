import unittest
import ksj
import os

print(f"ksj version: {ksj.__version__}")


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


class TestGetShp(unittest.TestCase):

    def test_zip(self):
        # 正常系、unzip = False
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        save_dir = "tests/shapefile"
        ksj.get_shp(url, save_dir=save_dir, unzip=False)
        has_zip = os.path.basename(url) in os.listdir(save_dir)
        name_without_extension = os.path.splitext(os.path.basename(url))[0]
        extract_path = os.path.join(save_dir, name_without_extension)
        is_extracted = os.path.exists(extract_path)
        self.assertTrue(has_zip)
        self.assertFalse(is_extracted)

    def test_unzip(self):
        # 正常系、unzip = True
        url = 'http://nlftp.mlit.go.jp/ksj/gml/data/A30a5/A30a5-11/A30a5-11_5340-jgd_GML.zip'
        save_dir = "tests/shapefile"
        ksj.get_shp(url, save_dir=save_dir, unzip=True)
        has_zip = os.path.basename(url) in os.listdir(save_dir)
        name_without_extension = os.path.splitext(os.path.basename(url))[0]
        extract_path = os.path.join(save_dir, name_without_extension)
        is_extracted = os.path.exists(extract_path)
        has_shp = [f for f in os.listdir(extract_path) if ".shp" in f]
        self.assertTrue(has_zip)
        self.assertTrue(is_extracted)
        self.assertTrue(len(has_shp) > 0)


class TestReadShp(unittest.TestCase):

    # TODO: 複数のshpが入ったzipの場合や、return_typeを変えたときの挙動
    def test_n03(self):
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        gdf = ksj.read_shp(url)
        actual = gdf.shape
        expected = (1525, 6)
        self.assertEqual(expected, actual)

    def test_n03_list(self):
        url = "http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2019/N03-190101_12_GML.zip"
        gdf = ksj.read_shp(url, return_type="list")
        actual = type(gdf)
        expected = list
        self.assertEqual(expected, actual)

    def test_a30(self):
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
        gdf = ksj.read_shp(url)[0]
        actual = ksj.translate(gdf).columns.tolist()
        expected = ['供用開始年', '設置期間(開始年)', '設置期間(終了年)', '関係ID',
                    '変遷ID', '変遷備考', '地点名', '接合部種別', 'geometry']
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
