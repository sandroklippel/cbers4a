# ![icon](cbers4a/cbers4a.svg) CBERS4A Downloader

Search and download CBERS4A imagery from INPE (Brazilian National Institute for Space Research). To download the images it is necessary to register at http://www2.dgi.inpe.br/catalogo/explore.

```
usage: cbers4a.pyz [-h] [--print | --download CREDENTIAL] [-i ITEM_ID]
                   [-c COLLECTION_ID] [--spat XMIN YMIN XMAX YMAX]
                   [--date BEGIN END] [--cloud_cover NUM]
                   [--path_row PATH ROW] [--limit LIMIT] [-t | --detail]
                   [-a ASSET_ID] [--save FILENAME] [-o /path/to/output/dir/]
                   [-l] [--version]

Search and download CBERS4A imagery from INPE

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list available collections and exit
  --version             show program's version number and exit

actions:
  --print               search and print a list with matched items (default)
  --download CREDENTIAL
                        search and download matched items

search options:
  -i ITEM_ID, --id ITEM_ID
                        item to return, ignores everything else
  -c COLLECTION_ID, --collection COLLECTION_ID
                        collection to search for items
  --spat XMIN YMIN XMAX YMAX
                        the area of interest (WGS84)
  --date BEGIN END      begin and end date given in the format YYYY-MM-DD
  --cloud_cover NUM     maximum cloud cover percentage
  --path_row PATH ROW   orbit (path) and scene center (row)
  --limit LIMIT         maximum number of items of each collection to return
                        (defaults to 10)

print options:
  -t, --total           suppress listing, show only the number of matched
                        items
  --detail              also lists available assets

download options:
  -a ASSET_ID, --asset ASSET_ID
                        download only specified asset (default: all)
  --save FILENAME       also save items as a FeaturesCollection GeoJSON file
  -o /path/to/output/dir/, --outdir /path/to/output/dir/
                        output directory
```