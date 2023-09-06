#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2020 Sandro Klippel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module documentation goes here
   and here
   and ...
"""

import argparse
import sys
import json
from datetime import datetime
from os.path import join
from tempfile import gettempdir

import requests


__author__ = "Sandro Klippel"
__copyright__ = "Copyright 2020, Sandro Klippel"
__license__ = "MIT"
__maintainer__ = "Sandro Klippel"
__email__ = "sandroklippel at gmail.com"
__status__ = "Prototype"
__revision__ = '$Format:%H$'


try:
    from tqdm import tqdm as ProgressBar
except ImportError:
    class ProgressBar(object):

        def __init__(self, **kwargs):
            self._total = kwargs.get('total', 0)
            self._desc = kwargs.get('desc', 'Filename.ext')
            self._downloaded = kwargs.get('initial', 0)

        def __enter__(self):
            print(
                "{description}, total size {total} bytes".format(
                    description=self._desc, total=self._total
                ),
                file=sys.stderr,
            )
            return self

        def __exit__(self, exception_type, exception_val, trace):
            print(file=sys.stderr)
            return True

        def update(self, b):
            """
            docstring
            """
            self._downloaded = self._downloaded + b
            print(
                "Downloading: {x} bytes".format(x=self._downloaded), end="\r", file=sys.stderr
            )


class Item(object):
    """Class to parse items from INPE STAC Catalog"""
    
    def __init__(self, feature):
        self._feature = feature

    def __str__(self):
        """
        docstring
        """
        row = "{id:<25s} {date:^10s} {cloud:>15.1f}".format
        return row(id=self.id, date=self.date, cloud=self.get_property('cloud_cover'))

    def _repr_html_(self):
        """
        html representation
        """

        html = f"""
        <html>
        <body>
        <img style="display: block; margin-left: auto; margin-right: auto;" src="{self.thumbnail}" width="296" border="0" />
        </body>
        </html> 
        """

        return html

    def __lt__(self, other):
        """
        docstring
        """
        return self.get_property('cloud_cover', 0) < other.get_property('cloud_cover', 0)

    @property
    def __geo_interface__(self):
        """
        Simple GeoJSON-like interface
        """
        return self._feature['geometry']

    @property
    def id(self):
        """
        Provider identifier globally unique. 
        """
        return self._feature['id']

    @property
    def date(self):
        """
        The acquisition date of the asset.
        """
        return self.get_datetime_fmt()

    @property
    def bbox(self):
        """
        Bounding Box of the asset.
        """
        return self._feature.get('bbox')

    @property
    def collection(self):
        """
        The id of the STAC Collection this Item references to.
        """
        return self._feature.get('collection')

    @property
    def thumbnail(self):
        """
        Thumbnail image link.
        """
        return self._feature['assets']['thumbnail']['href']

    @property
    def assets(self):
        """
        Unique keys of asset objects that can be downloaded.
        """
        return list(self._feature['assets'].keys())

    @property
    def cloud_cover(self):
        """
        Cloud coverage %
        """
        return self.get_property('cloud_cover')

    @property
    def path_row(self):
        """
        Return a string 'PATH_ROW'
        """
        return str(self.get_property('path','')) + '_' + str(self.get_property('row',''))

    @property
    def sensor(self):
        """
        Return the sensor
        """
        return self.get_property('sensor')

    @property
    def html(self):
        """
        Html to show image preview
        """

        return self._repr_html_()

    def get_datetime(self):
        """
        The acquisition date and time of the assets
        as an object of the class datetime.datetime.
        """
        try:
            return datetime.strptime(self.get_property('datetime'), '%Y-%m-%dT%H:%M:%S')
        except (ValueError, TypeError):
            return None

    def get_datetime_fmt(self, fmt='%Y-%m-%d'):
        """
        Return a string representing the acquisition date and time, controlled by a format string.
        """
        try:
            return self.get_datetime().strftime(fmt)
        except (AttributeError):
            return None

    def get_property(self, p, v=None):
        """
        Get additional metadata fields.
        None if it does not exist.
        """
        return self._feature['properties'].get(p, v)

    def url(self, asset):
        """
        Get asset url 
        """
        return self._feature['assets'][asset]['href']

    def download(self, asset, credential, outdir=gettempdir(), session=requests.Session()):
        """
        Download the asset.
        """
        url = self.url(asset)
        filename = url.split("/")[-1]
        outfile = join(outdir, filename)
        r = session.get(url, params={'email': credential, 'item_id': self.id, 'collection': self.collection}, stream=True, allow_redirects=True)
        if r.status_code == 200:
            total_size = int(r.headers.get('content-length'))
            initial_pos = 0
            with open(outfile,'wb') as f:
                with ProgressBar(total=total_size, unit='B', unit_scale=True, desc=filename, initial=initial_pos, ascii=True) as pb:
                    for ch in r.iter_content(chunk_size=4096): # (page size 4Kb)
                        if ch:
                            f.write(ch)
                            pb.update(len(ch))
            return outfile
        else:
            return 'ERROR in ' + url + ' (' + r.reason + ')'


class ItemCollection(object):
    """Class to parse json from INPE STAC Catalog"""

    def __init__(self, data):
        self._data = data
    
    @property
    def returned(self):
        return self._data['context']['returned']
    
    @property
    def matched(self):
        return self._data['context']['matched']

    @property
    def limit(self):
        return self._data['context']['limit']

    @property
    def complete(self):
        return self._data['context']['returned'] == self._data['context']['matched']

    @property
    def featurescollection(self): # FeaturesCollection GeoJSON ? ['type', 'id', 'geometry', 'bbox', 'properties']
        return {'type': 'FeatureCollection', 'features': list(self.features('type', 'id', 'geometry', 'bbox', 'properties'))}

    def items(self):
        for feat in self._data['features']:
            yield Item(feat)

    def features(self, *keys):
        keys = list(filter(lambda k: k in ['type', 'id', 'collection', 'geometry', 'bbox', 'properties', 'assets', 'links'], keys))
        if keys:
            for feat in self._data['features']:
                yield {key: feat[key] for key in keys}
        else:
            for feat in self._data['features']:
                yield feat

    def __len__(self):
        return self._data['context']['returned']

    def __getitem__(self, k):
        """
        docstring
        """
        try:
            return Item(next(filter(lambda i: i['id'] == k, self._data['features'])))
        except StopIteration:
            raise KeyError(k)

    def __contains__(self, k):
        """
        docstring
        """
        if isinstance(k, Item):
            return any(i['id'] == k.id for i in self._data['features'])
        else:
            return any(i['id'] == k for i in self._data['features'])

    def __iter__(self):
        """
        docstring
        """
        return self.items()


class Collections(object):
    """Simple class to parse collections json from INPE STAC"""
    
    def __init__(self, data):
        """
        docstring
        """
        self._data = data

    def __getitem__(self, k):
        """
        docstring
        """
        try:
            return next(filter(lambda i: i['id'] == k, self._data['collections']))
        except StopIteration:
            raise KeyError(k)

    def __iter__(self):
        """
        docstring
        """
        for i in [(collection['id'], collection['description']) for collection in self._data['collections']]:
            yield i

    def get_spatial_extent(self, id):
        """
        docstring
        """
        return self.__getitem__(id)['extent']['spatial']

    def get_temporal_extent(self, id):
        """
        docstring
        """
        return self.__getitem__(id)['extent']['temporal']

class Search(object):
    """Simple class to search INPE STAC Catalog"""
    
    # INPE STAC Catalog 
    base_url = 'http://www.dgi.inpe.br/lgi-stac'
    collection_endpoint = '/collections'
    search_endpoint = '/search'

    # http
    # timeout = 12

    def __init__(self, **default_search_keys):
        """
        Simple class to search INPE STAC Catalog.

            Parameters:
                str1 (str):The string which is to be reversed.

            Returns:
                reverse(str1):The string which gets reversed.
        """
        self.session = requests.Session()
        self._default_search_keys = default_search_keys
        self.search_keys = dict()
        self.update(**default_search_keys)

    def __call__(self, **search_keys):
        """
        docstring
        """
        query_keys = search_keys.pop('query', None)
        if query_keys is not None:
            self.query(**query_keys)
        self.update(**search_keys)
        if 'ids' in self.search_keys:
            features = []
            for id in self.search_keys['ids']:
                r = self.session.get(self.base_url + self.collection_endpoint + '/X/items/' + id)
                if r.status_code == 200:
                    feat = r.json()
                    if feat['type'] == 'Feature':
                        features.append(feat)
            return ItemCollection({"type": "FeatureCollection", "features": features})
        else:
            r = self.session.post(self.base_url + self.search_endpoint, json=self.search_keys)
            if r.status_code == 200:
                return ItemCollection(r.json())

    def update(self, **search_keys):
        """
        docstring
        """
        self.search_keys.update(search_keys)

    def defaults(self):
        """
        docstring
        """
        self.update(**self._default_search_keys)

    def clear(self):
        """
        docstring
        """
        self.search_keys = dict()

    def close(self):
        """
        docstring
        """
        self.session.close()
        self.session = None

    def query(self, **properties_keys):
        """
        docstring
        """
        if 'query' in self.search_keys:
            self.search_keys['query'].update(properties_keys)
        else:
            self.search_keys.update({'query': properties_keys})

    def bbox(self, bbox: list) -> None:
        """
        Only features that have a geometry that intersects the bounding box are selected

            Parameters:
                bbox (list): The bounding box provided as a list of four floats, 
                minimum longitude, minimum latitude, maximum longitude and maximum latitude.
        """
        self.update(bbox=bbox)

    def interval(self, interval):
        """
        docstring
        """
        self.update(datetime=interval)

    def date(self, start, end):
        """
        docstring
        """
        self.update(datetime=f'{start}T00:00:00Z/{end}T23:59:00Z')

    def intersects(self, intersects):
        """
        Only for future. Today, INPE-STAC does not support this feature.
        """
        self.update(intersects=intersects)

    def collections(self, collections):
        """
        docstring
        """
        self.update(collections=collections)

    def ids(self, ids):
        """
        docstring
        """
        self.update(ids=ids)

    def limit(self, limit):
        """
        docstring
        """
        self.update(limit=limit)

    def path_row(self, path, row):
        """
        docstring
        """
        self.query(path={'eq': path}, row={'eq': row})

    def cloud_cover(self, op, cloud_cover):
        """
        docstring
        """
        stac_op = {'>=': 'gte', '<=': 'lte', '=': 'eq', '>': 'gt', '<': 'lt'}
        try:
            self.query(cloud_cover={stac_op[op]: cloud_cover})
        except KeyError:
            pass
    
    @property
    def closed(self):
        """
        docstring
        """
        return self.session is None

    @staticmethod
    def get_collections():
        """
        docstring
        """
        with requests.get(url=Search.base_url + Search.collection_endpoint) as res:
            if res.status_code == 200:
                return Collections(res.json())

def parseargs():
    """parse command line arguments
    """

    # description
    parser = argparse.ArgumentParser(description='Search and download CBERS4A imagery from INPE', epilog=__copyright__)

    # actions group options
    actions_group = parser.add_argument_group('actions')
    mutual_group = actions_group.add_mutually_exclusive_group()
    mutual_group.add_argument('--print', dest='print', action='store_true', default=True, help='search and print a list with matched items (default)')
    mutual_group.add_argument('--download', dest='download', metavar='CREDENTIAL', type=str, help='search and download matched items')

    # search group options 
    search_group = parser.add_argument_group('search options')
    search_group.add_argument('-i', '--id', dest='ids', action='append', metavar='ITEM_ID', help='item to return, ignores everything else')
    search_group.add_argument('-c', '--collection', dest='collections', metavar='COLLECTION_ID', action='append', help='collection to search for items')
    search_group.add_argument('--spat', dest='bbox', metavar=('XMIN', 'YMIN', 'XMAX', 'YMAX'), nargs=4, type=float, help='the area of interest (WGS84)')
    # NOW can be used for the current day?
    search_group.add_argument('--date', dest='date', metavar=('BEGIN','END'), nargs=2, type=str, help='begin and end date given in the format YYYY-MM-DD')
    search_group.add_argument('--cloud_cover', dest='cloud_cover', metavar='NUM', type=int, help='maximum cloud cover percentage')
    search_group.add_argument('--path_row', dest='path_row', metavar=('PATH','ROW'), nargs=2, type=int, help='orbit (path) and scene center (row)')
    search_group.add_argument('--limit', dest='limit', type=int, metavar='LIMIT', default=10, help='maximum number of items of each collection to return (defaults to 10)')

    # print group options
    print_group = parser.add_argument_group('print options')
    listing_group = print_group.add_mutually_exclusive_group()
    listing_group.add_argument('-t', '--total', dest='total', action='store_true', default=False, help='suppress listing, show only the number of matched items')
    listing_group.add_argument('--detail', dest='detail', action='store_true', default=False, help='also lists available assets')

    # download group options
    download_group = parser.add_argument_group('download options')
    download_group.add_argument('-a', '--asset', dest='assets', metavar='ASSET_ID', action='append', help='download only specified asset (default: all)')
    download_group.add_argument('--save', dest='jsonfile', metavar='FILENAME', help='also save items as a FeaturesCollection GeoJSON file')
    download_group.add_argument('-o', '--outdir', dest='outdir', metavar='/path/to/output/dir/', help='output directory')

    # general options
    parser.add_argument('-l', '--list', dest='list_collections', action='store_true', help='list available collections and exit')
    parser.add_argument('--version', action='version', version=__version__)

    args = parser.parse_args()
    params = vars(args)
    return {k: params[k] for k in params.keys() if params[k] is not None}

def cli():
    """ command line interface
    """
    # get parameters 
    params = parseargs()
    # print(params)

    if params['list_collections']:
        # just list collections in INPE-STAC
        inpe_collections = Search.get_collections()
        print('{id:<20s} {desc:<50s}'.format(id='id', desc='description'))
        for id, description in inpe_collections:
            print(f'{id:<20s} {description:<50s}')
    else:
        init_keys = {k: params[k] for k in params.keys() if k in ['ids', 'collections', 'bbox', 'limit']}
        if params['total'] and 'download' not in params:
            init_keys.update({'limit': 0})
        search_inpe_stac = Search(**init_keys)
        if 'date' in params:
            search_inpe_stac.date(*params['date'])
        if 'cloud_cover' in params:
            search_inpe_stac.cloud_cover('<=', params['cloud_cover'])
        if 'path_row' in params:
            search_inpe_stac.path_row(*params['path_row'])
        # do search
        result = search_inpe_stac()
        # actions choice
        if 'download' in params:
            outdir = params.get('outdir', gettempdir())
            print(f'Downloading file(s) in the "{outdir}" directory:')
            for item in result:
                for asset in params.get('assets', item.assets):
                    item.download(asset, params['download'], outdir=outdir, session=search_inpe_stac.session)
            if 'jsonfile' in params:
                outfile = join(outdir, params['jsonfile'])
                with open(outfile, 'w') as json_file:
                    json.dump(result.featurescollection, json_file)
        elif params['total']:
            print(result.matched)
        else:
            head = "{id:<25s} {date:^10s} {cloud:>15s}".format(id='id', date='date', cloud='cloud cover (%)')
            print(head + '    assets' if params['detail'] else head)
            for item in result:
                print(str(item) + '    ' + ' '.join(item.assets) if params['detail'] else item)
            if not result.complete:
                print('Returned {0} scenes from {1} matched.'.format(result.returned, result.matched), 
                file=sys.stderr)
        search_inpe_stac.close()

        
if __name__ == "__main__":
    sys.exit(cli())
