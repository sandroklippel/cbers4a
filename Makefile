PLUGIN=qgis_cbers4a_downloader
ZIPFILE=$(PLUGIN).zip
PLUGIN_FILES=cbers4a/__init__.py                  \
             cbers4a/cbers4a.py                   \
             cbers4a/dockcbers4adownloader.py     \
             cbers4a/dockcbers4adownloaderbase.py \
             cbers4a/qgis_cbers4a_downloader.py   \
	     cbers4a/processing_algorithm.py      \
	     cbers4a/provider.py                  \
	     cbers4a/resources.py                 \
             cbers4a/metadata.txt                 \
             cbers4a/cbers4a.png                  \
	     cbers4a/grid/cbers4a_mux.json        \
	     cbers4a/grid/cbers4a_wfi.json

BUILD_FILES=cbers4a/__main__.py                  \
            cbers4a/cbers4a.py                   \

BUILD_DIR=build

APP=cbers4a.pyz

plugin: clean $(ZIPFILE)

clean:
	rm $(PLUGIN).zip

$(ZIPFILE): $(PLUGIN_FILES)
	zip $(ZIPFILE) $(PLUGIN_FILES)

ui: cbers4a/ui/dockcbers4adownloader.ui
	pyuic5 --from-imports --resource-suffix '' cbers4a/ui/dockcbers4adownloader.ui > cbers4a/dockcbers4adownloaderbase.py

resources: cbers4a/resources.qrc
	pyrcc5 -o cbers4a/resources.py cbers4a/resources.qrc

app: $(BUILD_FILES)
	rm -f $(APP)
	cp -p cbers4a/__main__.py build
	cp -p cbers4a/cbers4a.py build
	python3 -m zipapp -p "/usr/bin/env python3" -o $(APP) $(BUILD_DIR)
