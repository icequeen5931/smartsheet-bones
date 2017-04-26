================
Smartsheet Bones
================

A dead simple API client for Smartsheet.

.. code-block:: console

  Usage: smartbones.py [OPTIONS] COMMAND [ARGS]...

  Options:
    --help  Show this message and exit.

  Commands:
    add
    sheets
    token


List Sheets
-----------
Generates an enumerated list of sheet numbers & slug names

.. code-block:: console

    Usage: smartbones sheets



Get Rows in Sheet 
-----------------
The NAME can be a sheet number or a slug-name.  Use List Sheets above to
Show the available sheets.

.. code-block:: console

    Usage: smartbones sheets NAME


Set Smartsheet API Access Token
-------------------------------
Prompts for the access token, for security reasons the access token will
not be displayed.

.. code-block:: console

    Usage: smartbones token


Add Rows
--------
Takes a JSON array of objects and adds the rows to the specified sheet.
The NAME can be a sheet number or slug-name.  The FILE can be a filename
or left blank for STDIN. The dash character can also be used in place of
the FILE to indicate to force it to accept the data from STDIN. 

.. code-block:: console

    Usage: smartbones add NAME FILE


Update Rows
-----------
Under construction.
