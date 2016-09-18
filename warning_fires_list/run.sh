#!/bin/bash

send_error()
{
echo "`date +%Y.%m.%d-%T`: send_error(): ошибка при выполнении команды: ${1}" >> ${log}
echo "`date +%Y.%m.%d-%T`: send_error(): отправляю письмо пользователю: ${email_error_to}" >> ${log}
subject=`echo "OSM-сервер: ОШИБКА! Сбой анализа близости пожаров к объектам ОАО ДРСК"|base64 -w 0`
sendEmail -o tls=no -f osm_import@rsprim.ru -o message-charset=utf-8 -t "${email_error_to}" -s ${email_server} -u "=?utf-8?b?${subject}?=" \
-m "Письмо сгенерировано автоматически.
Произошёл сбой на сервере `hostname --fqdn` в подсистеме OSM. При попытке анализа близости пожаров к объектам ОАО ДРСК
произошла ошибка. Задачей скрипта было выяснение перечня объектов ОАО ДРСК, возле которых произошли возгорания.

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

# Анализ:
${parser} ${station_data_file} ${fires_data_file} ${station_warning_list}
if [ ! 0 -eq $? ]
then
	send_error "${parser} ${station_data_file} ${fires_data_file} ${station_warning_list}"
	exit 1
fi
${parser} ${tp_data_file} ${fires_data_file} ${tp_warning_list}
if [ ! 0 -eq $? ]
then
	send_error "${parser} ${tp_data_file} ${fires_data_file} ${tp_warning_list}"
	exit 1
fi
echo "`date +%Y.%m.%d-%T`: ============ success end $0 ==============" >> ${log}
exit 0
