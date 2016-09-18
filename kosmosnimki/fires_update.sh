#!/bin/bash

config_path="/opt/osm/openstreetmap.ru/OpenStreetMap.ru_dev/cron/config.sh"

source "${config_path}"

echo "`date +%Y.%m.%d-%T`: start $0" >> "${log}"
today="`date +%Y-%m-%d`"
yesterday="`date --date 'yesterday' +%Y-%m-%d`"

# Приморье:
url="http://maps.kosmosnimki.ru/rest/ver1/layers/F2840D287CD943C4B1122882C5B92565/search?query=%22DateTime%22%3E=%27${yesterday}%27%20and%20%22DateTime%22%3C=%27${today}%27%20&BorderFromLayer=78E56184F48149DF8A39BA81CA25A01E&BorderID=1&api_key=${API_KEY}"
temp="`mktemp /tmp/fire_osm_XXXXX`"
curl ${connect_opt} "${url}" -o "${temp}"
if [ 0 -eq $? ]
then
	echo "fire_test = `cat ${temp}`" > "${result}"
#cat "${temp}" >> "${result}"
	rm "${temp}"
	echo "`date +%Y.%m.%d-%T`: success update fire data for ${yesterday} - ${today} to file: ${result}" >> "${log}"
	exit 0
else
	echo "`date +%Y.%m.%d-%T`: ERROR update fire data for ${yesterday} - ${today}" >> "${log}"
	rm "${temp}"
	exit 1
fi

