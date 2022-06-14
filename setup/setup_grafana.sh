#!/bin/sh
mv /var/lib/grafana/plugins/* ./grafana-8.1.8/data/plugins/
python3 setup/import_folders.py
python3 setup/import_dashboards.py
python3 setup/add_data_source.py
echo "Please restart the docker container to apply the changes!"