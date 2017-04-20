import codecs
import json
import os
import sys

import click
import requests
from requests import RequestException, HTTPError


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
        click.echo(str(e), err=True)
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


def get_sheet_id(sheet_name, sheets):
    try:
        return get_sheets(sheets)[sheet_name]
    except KeyError as e:
        click.echo('ERROR: Sheet {} not found.'.format(e), err=True)
        sys.exit()


def get_sheets(sheets):
    return {i['name']: i['id'] for i in sheets.get('data', [])}


def get_rows(sheet, columns, disp_val=False, extra_keys=None):

    def map_columns(row, columns, val_key='value', extra_keys=None):
        cells = row.get('cells', [])
        data = {columns[cell['columnId']]: cell.get(val_key) for cell in cells}
        if extra_keys:
            data.update({k: row[k] for k in extra_keys if k in row})
        return data

    rows = sheet.get('rows', [])
    columns = {i['id']: i['title'] for i in sheet.get('columns', [])}
    val_key = 'displayValue' if disp_val else 'value'
    return [map_columns(row, columns, val_key, extra_keys) for row in rows]


def get_column_id(sheet, key):
    for column in sheet.get('columns', []):
        if column['title'] == key:
            return column['id']


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
@click.argument('sheet_name')
@click.argument('rows', type=click.File())
def add(sheet_name, rows):
    import pdb; pdb.set_trace()
    sheet_id = get_sheet_id(sheet_name, request('sheets'))
    columns = request('sheets/{}/columns'.format(sheet_id))
    data = add_rows(json.load(rows), columns)
    response = request('sheets/{}/rows'.format(sheet_id), data)
    click.echo(json.dumps(response, indent=2, sort_keys=True))


@cli.command()
@click.argument('sheet_name')
@click.option('-d', '--display', is_flag=True,
              help='Use display value instead of the raw value')
@click.option('-a', '--all', is_flag=True,
              help='Include the Sheet ID, Parent ID & Row Number')
@click.option('-i', '--id', is_flag=True,
              help='Include the Sheet ID')
@click.option('-p', '--parent', 'parentId', is_flag=True,
              help='Include the Parent ID')
@click.option('-r', '--rownum', 'rowNumber', is_flag=True,
              help='Include the Row Number')
def rows(sheet_name, display, **kwds):
    extra_keys = [k for k, v in kwds.items() if v]
    sheet_id = get_sheet_id(sheet_name, request('sheets'))
    columns = request('sheets/{}/columns'.format(sheet_id))
    sheet = request('sheets/{}'.format(sheet_id))
    rows = get_rows(sheet, columns, display, extra_keys)
    print(json.dumps(rows, indent=2, sort_keys=True))


@cli.command()
def sheets(id_):
    sheets_ = get_sheets(request('sheets'))
    if id_:
        width = len(max(map(str, sheets_.values()), key=len)) + 1
        for sheet, sheet_id in sorted(sheets_.items()):
            click.echo(str(sheet_id).ljust(width) + sheet)
    else:
        for sheet in sorted(sheets_):
            click.echo(sheet)


@cli.command()
@click.password_option()
def token(password):
    set_token(password)


if __name__ == '__main__':
    cli()
