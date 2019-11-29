# download all ksj dataset
import ksj
import time
from tqdm import tqdm
import pandas as pd
import os
import tempfile
import zipfile
from urllib.request import urlretrieve
import geopandas as gpd

save_dir = "data"



def get_shp(file_url: str, save_dir: str, save_file_name=None,
            unzip=False, silent=False):
    """指定したURLのzipファイルを指定フォルダにダウンロードする。

    Parameters
    ----------
    file_url : str
        国土数値情報ダウンロードサービスが提供するzipファイルのURL
    save_dir : str
        保存先ディレクトリのパス
    save_file_name : str
        保存するzipファイルの名前
    unzip : bool
        Trueの場合、zipファイルの解凍まで行います。
    silent : bool
        Trueの場合、ファイルをどこに解凍したかについての表示を無効にします。

    Returns
    -------
    None
    """
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if save_file_name is None:
        save_file_name = os.path.basename(file_url)
    elif re.search("(.zip)$", save_file_name) is None:
        save_file_name += ".zip"
    save_path = os.path.join(save_dir, save_file_name)
    urlretrieve(url=file_url, filename=save_path)
    if not silent:
        print(f"{save_file_name} is saved at {save_dir}")
    if unzip:
        name_without_extension = os.path.splitext(save_file_name)[0]
        extract_dir = os.path.join(save_dir, name_without_extension)
        if not os.path.exists(extract_dir):
            os.mkdir(extract_dir)
        with zipfile.ZipFile(save_path) as existing_zip:
            existing_zip.extractall(extract_dir)
        if not silent:
            print(f"{save_file_name} is extracted to {extract_dir}")


if __name__ == "__main__":
    # get all summary info
    summary = ksj.get_summary()
    summary.head()

    # get all urls (2min)
    urls_path = "unique_urls.csv"
    if os.path.exists(urls_path):
        print(f"loading {urls_path}")
        uniq_urls = pd.read_csv(urls_path)
    else:
        urls = pd.DataFrame()
        for i in tqdm(range(summary.shape[0])):
            url = ksj.get_url(identifier=summary.loc[i, "identifier"])
            urls = urls.append(url)
            time.sleep(0.5)
        # use unique urls by identifier and year
        uniq_urls = urls.drop_duplicates(
            ["identifier", "year"]).reset_index(drop=True)
        # zipfilename
        uniq_urls["zipfile_name"] = uniq_urls["zipFileUrl"].apply(
            lambda x: os.path.basename(x))
        # save
        print(f"saving {urls_path}")
        uniq_urls.to_csv(urls_path, index=False)
    
    for i in tqdm(uniq_urls.index):
        # get shapefile_name and shapefile_checksum
        url = uniq_urls.loc[i, "zipFileUrl"]
        get_shp(url, save_dir, unzip=True)
        time.sleep(0.5)


