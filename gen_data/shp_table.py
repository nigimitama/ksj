import requests
import hashlib
import ksj
import time
from tqdm import tqdm
import pandas as pd
import os
import tempfile
import zipfile
import urllib
import geopandas as gpd

# get tables to translate
# algorithm:
# 1. check shapefile_name or zip_file_name
#    - if shapefile_name or zipfile_name is known; then identifiable
# 2. check md5 checksum of first row of shapefile
#    - if it is known; then identifiable
# 3. else; then
#
# requirements for this algorithm:
# a table with following columns:
# - identifier
# - year
# - file_name of shp
# - md5 checksum of first row of shapefile


# generate shapefile data:

def read_shp_name(file_url) -> dict:
    """shapefileを読み込んで、ファイル名も返す"""
    save_file_name = os.path.basename(file_url)
    temp_dir = tempfile.TemporaryDirectory()
    save_dir = temp_dir.name
    save_path = os.path.join(save_dir, save_file_name)
    # download
    try:
        urllib.request.urlretrieve(url=file_url, filename=save_path)
        # unzip
        with zipfile.ZipFile(save_path) as existing_zip:
            existing_zip.extractall(save_dir)
        # load
        file_paths = _get_files(save_dir)
        shapefiles = [f for f in file_paths if f.endswith(".shp")]
        geojsons = [f for f in file_paths if f.endswith(".geojson")]

        # zipファイル内のファイル一覧情報も一応取得しておく
        result_base = {}
        result_base["file_names"] = [os.path.basename(f) for f in file_paths]
        result_base["shp_names"] = [os.path.basename(f) for f in shapefiles]
        result_base["n_shp"] = len(result_base["shp_names"])
        result_base["geojson_names"] = [os.path.basename(f) for f in geojsons]
        result_base["n_geojson"] = len(result_base["geojson_names"])

        if len(shapefiles) == 0:
            print(f"shapefile not found in {save_file_name}")
            results = pd.DataFrame()
        else:
            results = []
            for shp_path in shapefiles:
                result = result_base
                result["shp_name"] = os.path.basename(shp_path)
                gdf = _read_geofile(shp_path)
                if gdf is not None:
                    result["columns"] = gdf.columns.tolist()
                    result["nrows"] = gdf.shape[0]
                    result["ncols"] = gdf.shape[1]
                    if result["nrows"] > 0:
                        first_row_str = str(gdf.loc[0, :]).encode()
                        result["md5"] = hashlib.md5(first_row_str).hexdigest()
                    else:
                        result["md5"] = None
                results.append(result)
    except urllib.error.HTTPError:
        print(f"HTTP Error {file_url}")
        results = pd.DataFrame({"note": "HTTP Error"}, index=[0])
    temp_dir.cleanup()
    return results


def _read_geofile(file_path: str, verbose=1) -> gpd.GeoDataFrame:
    """
    geopandasで開ける地理データを読み込む
    既知の破損により読み込めないshpファイルは、同名のgeojsonがある場合そちらを読み込む
    """
    try:
        if verbose >= 2:
            print(f"reading a shapefile from {file_path}")
        gdf = gpd.read_file(file_path, encoding="CP932")
    except:
        import traceback
        traceback.print_exc()
        # A16-15_00_DID.shpはAttributeErrorで開けないが、同名のgeojsonは開ける
        # shpファイルと同名のgeojsonが同梱されているzipが124個ある
        # 'W05-08_24_GML.zip'はValueError: LineStrings must have at least 2 coordinate tuples
        if verbose >= 1:
            print(f"cannot read {file_path}")
        same_name_geojson = file_path.replace(".shp", ".geojson")
        if os.path.exists(same_name_geojson):
            if verbose >= 1:
                print(f"{same_name_geojson} found, trying to read it...")
            gdf = gpd.read_file(same_name_geojson, encoding="CP932")
            if verbose >= 1:
                print(f"done!")
        else:
            gdf = None
    return gdf


def _get_files(path: str) -> list:
    """get file paths recursively"""
    file_names = []
    for (root, _, files) in os.walk(path):
        for f in files:
            file_names.append(os.path.join(root, f))
    return file_names


def post_slack_message(message):
    api_url = "https://slack.com/api/chat.postMessage"
    token = os.environ["SLACK_TOKEN"]
    channel_id = "CNKS64RGB"  # 'log' channel
    params = {"token": token, "channel": channel_id,
              "text": message, "username": "notifier"}
    response = requests.post(api_url, data=params)
    if response.status_code != 200:
        print(f"[post_slack_message] status code: {response.status_code}")


def main():
    # get all summary info
    summary = ksj.get_summary()

    # get all urls
    urls_path = "ksj_urls.csv"
    if os.path.exists(urls_path):
        print(f"loading {urls_path}")
        urls = pd.read_csv(urls_path)
    else:
        print("get all urls")
        urls = pd.DataFrame()
        for i in tqdm(range(summary.shape[0])):
            url = ksj.get_url(identifier=summary.loc[i, "identifier"])
            urls = urls.append(url)
            time.sleep(0.1)
        # # use unique urls by identifier and year
        # uniq_urls = urls.drop_duplicates(
        #     ["identifier", "year"]).reset_index(drop=True)

        # zipfilename
        urls["zipfile_name"] = urls["zipFileUrl"]\
            .apply(lambda x: os.path.basename(x))
        urls = urls.reset_index(drop=True)
        # save
        print(f"saving {urls_path}")
        urls.to_csv(urls_path, index=False)

    # get shapefile_name and shapefile_checksum
    print("get shapefile_name")
    output_name = "unique_urls_hashes.csv"
    temp_output_name = output_name.replace(".csv", "")+"_temp.csv"
    
    if os.path.exists(temp_output_name):
        print(f"loading {temp_output_name}")
        ksj_data = pd.read_csv(temp_output_name)
        start_i = max(ksj_data["i"])+1
    else:
        ksj_data = pd.DataFrame()
        start_i = 0
    for i in tqdm(range(start_i, urls.index.stop)):
        row = urls.loc[[i], :]
        url = row["zipFileUrl"].values.item()
        # shapesは複数行であることもあり得る
        shapes = pd.DataFrame(read_shp_name(url))
        for col in row.columns:
            shapes[col] = row[col].values.item()  # 行数あわせ
        shapes["i"] = i
        # 結果の行に追加
        ksj_data = ksj_data.append(shapes)
        time.sleep(0.5)
        if i % 100 == 0:
            ksj_data.to_csv(temp_output_name, index=False)
    # column name 並べ替え
    added_cols = list(ksj_data.columns)
    for col in urls.columns:
        added_cols.remove(col)
    new_cols = list(urls.columns) + added_cols
    new_cols = ksj_data.filter(new_cols)
    # save
    print(f"saving {output_name}")
    ksj_data.to_csv(output_name, index=False)


if __name__ == "__main__":
    main()
    post_slack_message("show_table.py is finished!")

    # try:
    #     main()
    # except:
        # post_slack_message("show_table.py is finished!")
