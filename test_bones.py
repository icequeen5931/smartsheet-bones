import json
import os

import click
import pytest

from smartbones import (
    add_rows, get_contacts, get_columns, get_column_types, get_rows,
    get_sheet_id, get_sheets, get_token, set_token, update_rows
)

CUR_DIR = os.path.dirname(os.path.realpath(__file__)) + '\\testdata'
print(CUR_DIR)


def load(filename):
    return json.load(open(os.path.join(CUR_DIR, filename + '.json')))


def test_access_token():
    test_dir = '__test__bones__'
    set_token('12345', test_dir)
    assert get_token(test_dir) == '12345'
    os.remove(os.path.join(click.get_app_dir(test_dir), 'config'))
    os.rmdir(click.get_app_dir(test_dir))
    with pytest.raises(SystemExit):
        get_token(test_dir)


def test_get_sheets():
    result = {"sheet 1": 4583173393803140, "sheet 2": 2331373580117892}
    assert get_sheets(load('get_sheets')) == result
    assert get_sheets({}) == {}


def test_get_sheet_id():
    sheets = load('get_sheets')
    assert get_sheet_id('sheet 1', sheets) == 4583173393803140
    with pytest.raises(SystemExit):
        assert get_sheet_id('Sheet Not Found', sheets)


def test_get_columns():
    result = {7960873114331012: 'Favorite',
              642523719853956: 'Primary Column',
              5146123347224452: 'Status'}
    assert get_columns(load('get_columns')) == result
    assert get_columns({}) == {}


def test_get_column_types():
    result = {7960873114331012: 'CHECKBOX',
              642523719853956: 'TEXT_NUMBER',
              5146123347224452: 'PICKLIST'}
    assert get_column_types(load('get_columns')) == result
    assert get_column_types({}) == {}


def test_get_contacts():
    result = {'David Davidson': 'dd@example.com', 'Ed Edwin': 'ee@example.com'}
    assert get_contacts(load('get_contacts')) == result
    get_contacts({}) == {}


def test_get_rows():
    columns = load('get_columns')
    sheet = load('get_sheet')

    expected = [
        {
            'Favorite': False,
            'Primary Column': 'new value',
            'Status': 'new'
        }, {
            'Favorite': True,
            'Primary Column': 'desc_updated',
            'Status': 'completed'
        }
    ]
    assert get_rows(sheet, columns) == expected
    assert get_rows(sheet, columns, extra_keys=['bad key']) == expected

    expected = [
        {
            'Favorite': None,
            'Primary Column': 'new value',
            'Status': 'new'
        }, {
            'Favorite': None,
            'Primary Column': 'desc_updated',
            'Status': 'completed'
        }
    ]
    assert get_rows(sheet, columns, disp_val=True) == expected

    expected = [
        {
            'id': 3326917907257764,
            'rowNumber': 1,
            'Favorite': False,
            'Primary Column': 'new value',
            'Status': 'new'
        }, {
            'id': 5584117714643912,
            'parentId': 3326917907257764,
            'rowNumber': 2,
            'Favorite': True,
            'Primary Column': 'desc_updated',
            'Status': 'completed'
        }
    ]
    extra_keys = ['id', 'parentId', 'rowNumber']
    assert get_rows(sheet, columns, extra_keys=extra_keys) == expected


def test_add_rows():
    data = [{'Favorite': False, 'Primary Column': 'newer status'},
            {'Favorite': True, 'Primary Column': 'updated row'}]
    columns = load('get_columns')
    expected = load('add_rows')
    assert add_rows(columns, data) == expected


def test_update_rows():
    sheet = load('get_sheet')
    expected = load('update_rows')
    key = 'Primary Column'
    data = [{
        "Favorite": True,
        "Primary Column": "new value"
    }, {
        "Favorite": False,
        "Primary Column": "desc_updated",
        "Status": "In Progress"
    }]
    assert update_rows(sheet, data, key=key, strict=False) == expected

    data = [{"Favorite": True, "Primary Column": "missing key"}]
    assert update_rows(sheet, data, key=key, strict=False) == []
