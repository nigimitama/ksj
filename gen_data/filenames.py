import os
import pandas as pd

def _get_files(path: str) -> list:
    """get file pathes recursively"""
    file_names = []
    for (root, _, files) in os.walk(path):
        for f in files:
            file_names.append(os.path.join(root, f))
    return file_names

n_zip = len(os.listdir("data"))
print(f"{n_zip} zips")

file_names = _get_files("data")

# csv書き出し１
splited_names = [f.split("\\") for f in file_names]
pd.DataFrame(splited_names).to_csv("names.csv",index=False)

# csv書き出し２
rows = []
for f in file_names:
    row = {}
    row["file_path"] = f
    row["dir"] = os.path.dirname(f)
    row["file_name"] = os.path.basename(f)
    row["extension"] = os.path.splitext(row["file_name"])[-1]
    rows.append(row)
file_pathes = pd.DataFrame(rows)
file_pathes.to_csv("file_path_names.csv",index=False)

# 一つのdirectoryにいくつのshpが入っているのか
has_shpes = file_pathes.query("extension == '.shp'")
shp_counts = (has_shpes["dir"] + has_shpes["extension"]).value_counts().to_frame("count")
table = shp_counts["count"].value_counts().reset_index().rename(columns={"index": "1zipあたりのshpの数", "count": "zipの数"})
table.to_csv("how_many_shp_in_zip.csv",index=False)


geofiles = [f for f in file_names if (".shp" in f) or (".geojson" in f)]
print(f"{len(geofiles)}files")

shapefiles = [f for f in file_names if (".shp" in f)]
print(f"{len(shapefiles)} shp files")

geojsons = [f for f in file_names if (".geojson" in f)]
print(f"{len(geojsons)} geojson files")

shp_names = [f.replace(".shp", "") for f in geojsons]

geojson_names = [f.replace(".geojson", "") for f in geojsons]

# いくつのgeojsonが同梱されているか
same_names_geojson = []
for g in geojson_names:
    for s in shapefiles:
        if g in s:
            same_names_geojson.append(s)
print(f"{len(same_names_geojson)} same_names files")
print(f"{len(set(same_names_geojson))} unique same_names files")

# 同名のshapefile
same_names_shp = []
for s in shp_names:
    for g in geojsons:
        if s in g:
            same_names_shp.append(g)
print(f"{len(same_names_shp)} same_names files")
print(f"{len(set(same_names_shp))} unique same_names files")

# 130あるgeojsonは重複を除けば124で、124個についてはすべて同じ名前のshpがある
# geojson だけしかない、というものはない
shp_same_name_with_gj = set([f.replace(".shp", "") for f in same_names_geojson])
gj_same_name_with_shp =  set([f.replace(".geojson", "") for f in same_names_shp])
print(f"{len(shp_same_name_with_gj & gj_same_name_with_shp)} common names")


[f for f in file_names if ("S05-d-14_GML" in f)]
