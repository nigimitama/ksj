# ksj

[![CircleCI](https://circleci.com/gh/nigimitama/ksj/tree/master.svg?style=svg)](https://circleci.com/gh/nigimitama/ksj/tree/master)

[国土数値情報ダウンロードサービス](http://nlftp.mlit.go.jp/ksj/index.html)のWeb APIを簡単に扱うためのPythonパッケージです。

データ分析での利用を想定しており、本パッケージのメソッドの返り値はpandasやgeopandasのオブジェクトになります。



## インストール方法

```
pip install ksj
```

⚠️Windowsの場合[geopandasの依存パッケージ](http://geopandas.org/install.html#installing-with-pip)がpipではインストールできないため、**先にそちらをインストールする必要があります。** ご注意ください。

UNIX系OSの場合、`pip install ksj`だけでgeopandasもインストールされます。



## ドキュメント

使用方法は[ksj documentation](https://nigimitama.github.io/ksj/)をご覧ください



## 利用上の注意

APIの利用やAPIで得られる国土数値情報の利用にあたっては、国土数値情報ダウンロードサービスの利用約款および同Web APIの利用規約をご確認の上ご利用ください。

- http://nlftp.mlit.go.jp/ksj/other/yakkan.html
- http://nlftp.mlit.go.jp/ksj/api/about_api.html


