#!/bin/bash

send_error()
{
echo "`date +%Y.%m.%d-%T`: send_error(): ошибка при выполнении команды: ${1}" >> ${log}
echo "`date +%Y.%m.%d-%T`: send_error(): отправляю письмо пользователю: ${email_error_to}" >> ${log}
subject=`echo "OSM-сервер: ОШИБКА! Сбой обновления данных о пожарах"|base64 -w 0`
sendEmail -o tls=no -f abuse@rsprim.ru -o message-charset=utf-8 -t "${email_error_to}" -s ${email_server} -u "=?utf-8?b?${subject}?=" \
-m "Письмо сгенерировано автоматически.
Произошёл сбой на сервере `hostname` в подсистеме OSM. При попытке обновления данных о пожарах
произошла ошибка. Задачей обновления было регулярное обновление данных, преобразование их в нужный формат и
отображение данных о пожарах на карте. В данный момент данные о пожарах на карте либо не отображаются, либо устарели.

======== Техническая информация: ========
Сбой произошёл при выполнении команды: 
${1}

В обычной ситуации данная команда не должна завершаться с ошибкой. Значит на то были веские причины.

Последние строки лога этого ($0) скрипта:
`tail -n 20 ${log}`
" &>> ${log}
}

if [ -z ${1} ]
then
	echo "Нужен один аргумент - конфиг-файл"
	exit 1
fi

source "${1}"

echo "`date +%Y.%m.%d-%T`: ============ start $0 ==============" >> ${log}

# Данные от NASA:
# https://earthdata.nasa.gov/data/near-real-time-data/firms/active-fire-data#tab-content-7
# KML:
#wget https://firms.modaps.eosdis.nasa.gov/active_fire/kml/Russia_and_Asia_24h.kml
# TXT:
rm "${import_data_file}"
#wget -q https://firms.modaps.eosdis.nasa.gov/active_fire/text/Russia_and_Asia_24h.csv -O "${import_data_file}"
curl --insecure --proxy1.0 prx.rs.int:3128 https://firms.modaps.eosdis.nasa.gov/active_fire/text/Russia_and_Asia_24h.csv -o "${import_data_file}"

if [ ! 0 -eq $? ]
then
	send_error "wget https://firms.modaps.eosdis.nasa.gov/active_fire/text/Russia_and_Asia_24h.csv -O ${import_data_file}"
	exit 1
fi
size="`stat -c %s ${import_data_file}`"
echo "`date +%Y.%m.%d-%T`: успешно скачали данные о пожарах. Файл создан: `stat -c %z ${import_data_file}`, размер: $size байт" >> ${log}
if [ 0 -eq $size ]
then
	echo "`date +%Y.%m.%d-%T`: скачанный файл нулевого размера - ОШИБКА!" >> ${log}
	send_error "wget https://firms.modaps.eosdis.nasa.gov/active_fire/text/Russia_and_Asia_24h.csv -O ${import_data_file}"
	exit 1
fi

# Конвертация:
${parser} ${import_data_file} ${out_file}
if [ ! 0 -eq $? ]
then
	send_error "${parser} ${import_data_file} ${out_file}"
	exit 1
fi
echo "`date +%Y.%m.%d-%T`: ============ success end $0 ==============" >> ${log}
exit 0
