import codecs
import json
import os
import sys

import click
import requests
from requests import RequestException, HTTPError


def request(url, data=None):
    url = 'https://api.smartsheet.com/2.0/' + url
    hdr = {'Authorization': 'Bearer ' + get_token()}
    params = {'includeAll': True}
    request = getattr(requests, ('post' if data else 'get'))
    try:
        response = request(url, headers=hdr, params=params)
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


def add_rows(rows, columns, to_top=True):
    columns = {v: k for k, v in get_columns(columns)}
    return [{'cells': [{'columnId': columns[k], 'value': v}
            for k, v in row.items() if k in columns]} for row in rows]


def get_columns(columns):
    return {i['id']: i['title'] for i in columns.get('data', [])}


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


def map_columns(row, columns, val_key='value', extra_keys=None):
    cells = row.get('cells', [])
    data = {columns[cell['columnId']]: cell.get(val_key) for cell in cells}
    if extra_keys:
        data.update({k: row[k] for k in extra_keys if k in row})
    return data


def get_rows(sheet, columns, disp_val=False, extra_keys=None):
    rows = sheet.get('rows', [])
    columns = get_columns(columns)
    val_key = 'displayValue' if disp_val else 'value'
    return [map_columns(row, columns, val_key, extra_keys) for row in rows]


@click.group()
def cli():
    pass


@cli.command()
@click.argument('sheet_name')
@click.argument('rows')
def add(sheet_name, rows):
    sheet_id = get_sheet_id(sheet_name, request('sheets'))
    columns = request('sheets/{}/columns'.format(sheet_id))
    data = add_rows(rows, columns)
    response = request('sheets/{}/rows'.format(sheet_id), data)
    click.echo(json.dumps(response, index=True))


@cli.command()
@click.option('-i', '--id', 'id_', is_flag=True, help='Show Sheet IDs')
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
@click.argument('sheet_name')
@click.option('-d', '--display', is_flag=True,
              help='Use display value instead of the raw value')
@click.option('-i', '--id', is_flag=True,
              help='Include the Sheet ID')
@click.option('-p', '--parent', 'parentId', is_flag=True,
              help='Include the parent ID')
@click.option('-r', '--rownum', 'rowNumber', is_flag=True,
              help='Include the row number')
def sheet(sheet_name, display, **kwds):
    extra_keys = [k for k, v in kwds.items() if v]
    sheet_id = get_sheet_id(sheet_name, request('sheets'))
    columns = request('sheets/{}/columns'.format(sheet_id))
    sheet = request('sheets/{}'.format(sheet_id))
    rows = get_rows(sheet, columns, display, extra_keys)
    click.echo(json.dumps(rows, indent=2, sort_keys=True))


@cli.command()
@click.password_option()
def token(password):
    set_token(password)

if __name__ == '__main__':
    cli()
