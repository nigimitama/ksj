Installation
============

インストール方法
----------------

.. code-block:: shell

    pip install ksj

.. note::

   ⚠️Windowsの場合 `geopandasの依存パッケージ <https://geopandas.org/install.html#installing-with-pip>`__ がpipではインストールできないため、先にそちらをインストールする必要があります。 ご注意ください。

UNIX系OSの場合、pip install ksjだけでgeopandasもインストールされます。


必要環境
--------
Python 3.6以上


依存パッケージ
--------------
本パッケージは以下のパッケージを使用します。

.. code-block::

    lxml>=4.4.0
    xmljson>=0.2.0
    xlrd>=1.2.0
    geopandas>=0.6.0
