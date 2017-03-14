================
Smartsheet Bones
================

A dead simple API client for Smartsheet.

.. code-block:: console

    Usage: smartbones [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      add
      sheet
      sheets
      token


List Sheets
-----------

.. code-block:: console

    Usage: smartbones sheets [OPTIONS]

    Options:
      -i, --id  Show Sheet IDs
      --help    Show this message and exit.


Get Rows in Sheet 
-----------------

.. code-block:: console

    Usage: smartbones sheet [OPTIONS] SHEET_NAME

    Options:
      -d, --display  Use display value instead of the raw value
      -i, --id       Include the Sheet ID
      -p, --parent   Include the parent ID
      -r, --rownum   Include the row number
      --help         Show this message and exit.


Set Smartsheet API Access Token
-------------------------------

.. code-block:: console

    Usage: smartbones token [OPTIONS]

    Options:
      --password TEXT
      --help           Show this message and exit.


Add Rows
--------
Under construction.


Update Rows
-----------
Under construction.
