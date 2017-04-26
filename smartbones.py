import codecs
import json
import os
import sys

import click
import requests
from requests import RequestException, HTTPError

from slugs import slugify
from textmenu import get_colored_enumerated_list


def package_request(url, data, access_token):
    url = 'https://api.smartsheet.com/2.0/' + url
    auth = 'Bearer ' + access_token
    headers = {'Authorization': auth, 'Content-Type': 'application/json'}
    params = {}
    if data:
        method = 'post'
        data = json.dumps(data)
    else:
        method = 'get'
        params['includeAll'] = True
    return method, url, {'data': data, 'headers': headers, 'params': params}


def request(url, data=None):
    method, url, kwds = package_request(url, data, get_token())
    try:
        response = getattr(requests, method)(url, **kwds)
        response.raise_for_status()
        return response.json()
    except (RequestException, HTTPError, TypeError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def get_token(app_dir='Bones'):
    cfg = os.path.join(click.get_app_dir(app_dir), 'config')
    try:
        return codecs.decode(open(cfg).read(), 'rot-13')
    except EnvironmentError:
        click.echo('Access token not set.', err=True)
        sys.exit(1)


def set_token(access_token, app_dir='Bones'):
    app_dir = click.get_app_dir(app_dir)
    cfg = os.path.join(app_dir, 'config')
    try:
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
        with open(cfg, 'w') as file_:
            file_.write(codecs.encode(access_token, 'rot-13'))
            click.echo('Access token saved.')
    except EnvironmentError as e:
        click.echo(str(e), err=True)


def get_column_types(columns):
    return {i['id']: i['type'] for i in columns.get('data', [])}


def get_contacts(contacts):
    return {i['name']: i['email'] for i in contacts.get('data', [])}


def get_sheets(sheets):
    return {i['name']: i['id'] for i in sheets.get('data', [])}


def get_rows(sheet):

    def map_cells(row, columns):
        cells = row.get('cells', [])
        row['values'] = {columns[c['columnId']]: c['value']
                         for c in cells if 'value' in c}
        row['displayValues'] = {columns[c['columnId']]: c.get('displayValue')
                                for c in cells if 'displayValue' in c}
        del row['cells']
        return row

    rows = sheet.get('rows', [])
    columns = {i['id']: i['title'] for i in sheet.get('columns', [])}
    return [map_cells(row, columns) for row in rows]


def get_column_id(sheet, key):
    for column in sheet.get('columns', []):
        if column['title'] == key:
            return column['id']


def get_sheet_id(name):
    sheets_ = request('sheets').get('data', [])
    names = slugify([i['name'] for i in sheets_])
    try:
        index = int(name) - 1 if name.isdigit() else names.index(slugify(name))
        return sheets_[index]['id']
    except (IndexError, ValueError):
        print('Sheet not found.', file=sys.stderr)
        sys.exit(1)


def add_rows(data, columns, to_top=True, strict=False):

    def set_cells(columns, key, value, strict):
        return {'columnId': columns[key], 'value': value, 'strict': strict}

    def add_row(columns, row, to_top, strict):
        cells = [set_cells(columns, k, v, strict)
                 for k, v in row.items() if k in columns]
        return {'toTop': to_top, 'cells': cells}

    columns = {i['title']: i['id'] for i in columns.get('data', [])}
    return [add_row(columns, i, to_top, strict) for i in data]


def update_rows(sheet, updates, key=None, strict=False):

    def get_row_id(rows, key_id, value):
        for row in rows:
            for cell in row['cells']:
                if (cell['columnId'] == key_id and cell['value'] == value):
                    return row['id']

    def set_cells(columns, key, value, strict):
        return {'columnId': columns.get(key), 'value': value, 'strict': strict}

    def update_row(rows, columns, new_row, key, key_id, strict):
        value = new_row.get(key)
        cells = [set_cells(columns, k, v, strict) for k, v in new_row.items()]
        row_id = get_row_id(rows, key_id, value)
        if row_id is not None:
            return {'id': row_id, 'cells': cells}

    rows = sheet.get('rows', [])
    cols = {i['title']: i['id'] for i in sheet.get('columns', [])}
    key_id = cols.get(key)
    if key_id:
        results = [update_row(rows, cols, i, key, key_id, strict)
                   for i in updates]
        return [i for i in results if i is not None]


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.argument('rows', type=click.File())
def add(name, rows):
    id_ = get_sheet_id(name)
    columns = request('sheets/{id_}/columns'.format(id_=id_))
    data = add_rows(json.load(rows), columns)
    response = request('sheets/{id_}/rows'.format(id_=id_), data)
    click.echo(json.dumps(response, indent=2, sort_keys=True))


@cli.command()
@click.argument('name', nargs=-1)
def sheets(name):
    if name:
        id_ = get_sheet_id(name[0])
        sheet = request('sheets/{id_}'.format(id_=id_))
        rows = get_rows(sheet)
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        sheets_ = request('sheets')
        names = slugify([i['name'] for i in sheets_.get('data', [])])
        for sheet in get_colored_enumerated_list(names):
            click.echo(sheet)


@cli.command()
@click.password_option()
def token(password):
    set_token(password)


if __name__ == '__main__':
    cli()
