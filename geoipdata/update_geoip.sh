#!/bin/bash

cd "$(dirname "$0")"

wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz

tar -zxvf GeoLite2-City.tar.gz --strip=1

rm *.txt *.tar.gz