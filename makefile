PLUGIN=qgis_cbers4a_downloader
ZIPFILE=$(PLUGIN).zip
PLUGIN_FILES=cbers4a/__init__.py                  \
             cbers4a/cbers4a.py                   \
             cbers4a/dockcbers4adownloader.py     \
             cbers4a/dockcbers4adownloaderbase.py \
             cbers4a/qgis_cbers4a_downloader.py   \
             cbers4a/metadata.txt                 \
             cbers4a/cbers4a.svg

plugin: clean $(ZIPFILE)

clean:
	rm $(PLUGIN).zip

$(ZIPFILE): $(PLUGIN_FILES)
	zip $(ZIPFILE) $(PLUGIN_FILES)

ui: dockcbers4adownloader.ui
    pyuic5 --from-imports --resource-suffix '' dockcbers4adownloader.ui > dockcbers4adownloaderbase.py