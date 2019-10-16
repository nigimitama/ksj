FROM python:3

RUN apt update -y && apt upgrade -y
RUN pip3 install numpy pandas shapely fiona pyproj six descartes
RUN pip3 install git+https://github.com/geopandas/geopandas.git
RUN pip3 install kokudo-suuchi-jouhou
