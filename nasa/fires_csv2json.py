#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
import time
import calendar
import fires_csv2json_conf as conf


def write_header(f):
	header=u"""fire_test = {
	"type": "FeatureCollection",
	"features": [
"""
	f.write(header)
	
def write_end(f):
	header=u"""\n
	]
}
"""
	f.write(header)
	
def write_item(f,latitude,longitude,brightness,scan,track,satellite,confidence,version,bright_t31,frp,descr,DateTime):
	if satellite == "A":
		satellite="Aqua"
	elif satellite == "T":
		satellite="Terra"
	else:
		satellite="Неизвестно"
		
	#"Town": "null"
	#"ClusterID": 41206452,
	#"FireType": 4,
	#"HotSpotID": 0,
	#"Sample": 1542,
	#"DataSource": "IRK",
	header=u"""	{
		"type": "Feature",
		"geometry": {
			"type": "Point",
				"coordinates": [
				%(longitude)f,
				%(latitude)f
				]
		},
		"properties": {
			"Platform": "%(satellite)s",
			"Confidence": %(confidence)s,
			"Power": %(power)f,
			"DateTime": "%(DateTime)s",
			"Descr": "%(descr)s"
		}
	}""" % {
		"latitude":latitude,\
		"longitude":longitude,\
		"satellite":satellite,\
		#brightness,scan,track,acq_date,acq_time,satellite,version,	bright_t31,
		"confidence":confidence,\
		"DateTime":DateTime,\
		"descr":descr,\
		"power":frp \
	}
	f.write(header.encode('utf-8'))
	



if len(sys.argv) < 3:
	print("нужно два параметра: входной и выходной файл\n")
	sys.exit(1)

in_file=sys.argv[1]
out_file=sys.argv[2]


x=0
f=open(out_file,"w+")
write_header(f)
# The attribute fields are as follows:
# 1. Latitude
# 2. Longitude
# 3. Brightness Temperature (Kelvin)
# 4. Along scan pixel size
# 5. Along track pixel size
# 6. Date of acquisition
# 7. Time of acquisition (UTC)
# 8. Satellite (A=Aqua and T=Terra)
# 9. Confidence (0 – 100%)
# 10. Version (Collection and source)
# 11. Brightness T31 (Kelvin)
# 12. FRP (Fire Radiative Power) (MW)
#latitude,	longitude,	brightness,	scan,	track,	acq_date,	acq_time,	satellite,	confidence,	version,	bright_t31,	frp
# 44.375,	132.321,	310.4,		1.5,	1.2,	2015-04-29,	0150,		T,			38,			5.0       ,	293.5,		14.8

time_window_sec=conf.time_window * 3600

for line in open(in_file):
  try:
    latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp=line.split(",")
  except:
    continue
  if latitude == "latitude":
    # пропуск заголовка
    continue
  latitude_f=float(latitude)
  longitude_f=float(longitude)
  # Убираем перенос строки:
  frp=float(frp.split("\n")[0])
  if frp >50 and frp < 100:
    descr=u"средний пожар"
  elif frp >= 100 and frp < 300:
    descr=u"сильный пожар"
  elif frp >= 300:
    descr=u"очень сильный пожар"
  else:
    descr=u"слабый пожар"

  #2015-04-29, 0150
  time_format='%Y-%m-%d  %H%M'
  str_time= acq_date + " " + acq_time
  # разбираем дату от наса в структуру времени:
  sys_time_utc=time.strptime(str_time, time_format)
  # структуру времени в unix-время в секундах в UTC:
  time_s_utc=calendar.timegm(sys_time_utc)
  # UTC unix-время в секундах в структуру локального времени:
  sys_time_local=time.localtime(time_s_utc)
  #print("utc: ", time.strftime("%Y-%m-%d %H:%M:%S", sys_time_utc ))
  #print("local: ", time.strftime("%Y-%m-%d %H:%M:%S", sys_time_local ))
  DateTime=time.strftime("%d.%m.%Y %H:%M", sys_time_local)

  if time.time()-time_s_utc > time_window_sec:
    # Данные старее time_window (опция в конфиге) часов - пропускаем:
    continue

  # Фильтруем:
  if longitude_f>conf.bbox[0] and longitude_f < conf.bbox[2] and latitude_f > conf.bbox[1] and latitude_f < conf.bbox[3]:
    if x > 0:
      # Ставим запятую:
      f.write(",\n")
    write_item(f,latitude_f,longitude_f,brightness,scan,track,satellite,confidence,version,bright_t31,frp,descr,DateTime)
    x+=1
write_end(f)
f.close()

