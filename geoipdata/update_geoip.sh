#!/bin/bash

cd "$(dirname "$0")"

wget "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=k6NcBvYRk76uZyhw&suffix=tar.gz" -O GeoLite2-City.tar.gz

tar -zxvf GeoLite2-City.tar.gz --strip=1

rm *.txt *.tar.gz