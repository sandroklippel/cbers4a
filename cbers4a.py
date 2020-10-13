from datetime import datetime
from os.path import basename, join
from shutil import copyfileobj
from tempfile import gettempdir

import requests


class Collections(object):
    pass


class Item(object):
    """Class to parse items from INPE STAC Catalog"""
    
    def __init__(self, feature):
        self._feature = feature

    def __str__(self):
        """
        docstring
        """
        return "{0}\t{1}\t{2:.1f}%\t{3} asset(s)".format(self.id, self.date, self.get_property('cloud_cover'), len(self.assets))

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
        Unique keys of the dictionary of asset objects that can be downloaded.
        """
        return self._feature['assets'].keys()

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

    def download(self, asset, credential, outdir=gettempdir(), session=requests.Session()):
        """
        Download the asset.
        """
        url = self._feature['assets'][asset]['href']
        filename = basename(url)
        outfile = join(outdir, filename)
        with session.get(url, params={'key': credential}, stream=True) as r:
            if r.status_code == 200:
                with open(outfile, 'wb') as f:
                    copyfileobj(r.raw, f)
                return outfile
            else:
                return r.reason


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


class Search(object):
    """Simple class to search INPE STAC Catalog"""
    
    # INPE STAC Catalog 
    base_url = 'http://www2.dgi.inpe.br/inpe-stac/stac'
    collection_endpoint = '/collections'
    search_endpoint = '/search'

    # http
    timeout = 12

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
        r = self.session.post(self.base_url + self.search_endpoint, json=self.search_keys)
        if r.status_code == 200:
            return ItemCollection(r.json())
        else:
            return r.reason

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
        self.update(time=interval)

    def date(self, start, end):
        """
        docstring
        """
        self.update(time=f'{start}T00:00:00/{end}T23:59:00')

    def intersects(self, intersects):
        """
        docstring
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


    #     bbox list float Only features that have a geometry that intersects the bounding box are selected
    #     datetime str Either a date-time or an interval, open or closed. Date and time expressions adhere to RFC 3339.
    #     intersects GeoJSON
    #     collections list str Collection IDs to include in the search for items.
    #     ids list int Array of Item ids to return. All other filter parameters that further restrict the number of search results are ignored
    #     limit int The maximum number of results to return
    #     query dict Define which properties to query and the operations to apply
    #         ('datetime', 'path', 'row', 'satellite', 'sensor', 'cloud_cover', 'sync_loss')
    #     """
    #        {"query":{"cloud_cover":{"lte":50}},
    #         "bbox":[-52.37132302,-26.41049765,-50.64136522,-25.41363448],
    #         "time":"2020-01-01T00:00:00/2020-09-30T23:59:00",
    #         "collections": ['CBERS4A_WPM_L4_DN'],
    #         "limit":100}

def cli(parameter_list):
    """
    docstring
    """
    pass
        
if __name__ == "__main__":
    cli()