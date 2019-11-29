# download all ksj dataset
import ksj
import time
from tqdm import tqdm
import pandas as pd
import os

# get all summary info
summary = ksj.get_summary()
summary.head()

# get all urls
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
    url = uniq_urls.loc[i, "zipFileUrl"]
    gdfs = ksj.read_shp(url)
    if type(gdfs) is list:
        for gdf in gdfs:
            print(gdf.head(1))
    else:
        print(gdfs.head(1))
    time.sleep(0.5)
