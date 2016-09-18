#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
import time
import calendar
import generate_warning_fires_list_config as conf
import great_circles as great_circles


def write_file(out_file,warning_list):
	f=open(out_file,"w+")
	x=0
	for obj in warning_list:
		data=u"""%(name)s|%(lon)f|%(lat)f|%(distance)f|%(date)s""" % {"name":obj["name"].decode('utf-8'), "lon":obj["lon"], "lat":obj["lat"], "distance":obj["fire_distance"], "date":obj["fire_date"]}
		if x != 0:
			f.write(u"\n")
		f.write(data.encode("utf-8"))
		x+=1
	f.close()

def get_near_object(data_file,fire_lat,fire_lon):
	for line in open(data_file,"r"):
		obj_lon,obj_lat,obj_name=line.split("|")
		obj_name=obj_name.split("\n")[0]
		fire_distance=great_circles.get_dist(float(obj_lon), float(obj_lat),fire_lon, fire_lat)
		if conf.DEBUG:
			print("Расстояние от пожара до объекта с именем '%s' = %f" % (obj_name, fire_distance) )
		if (conf.min_fire_distance > fire_distance):
			obj={}
			obj["lon"]=float(obj_lon)
			obj["lat"]=float(obj_lat)
			obj["name"]=obj_name
			obj["fire_distance"]=fire_distance
			yield obj


if len(sys.argv) < 4:
	print("Необходимо 3 параметра: файл данных с корпоративными данными, файл данных с пожарами, выходной файл\n")
	sys.exit(1)

corp_data_file=sys.argv[1]
fires_data_file=sys.argv[2]
out_file=sys.argv[3]

if len(sys.argv) < 3:
	print("нужно два параметра: входной и выходной файл\n")
	sys.exit(1)

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
if conf.DEBUG:
	print("Обрабатываем список пожаров")
warning_list=[]
for line in open(fires_data_file):
  if conf.DEBUG:
    print("запись пожара: %s" % line)
  try:
    latitude,longitude,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp=line.split(",")
    if latitude == "latitude":
      # пропуск заголовка
      continue
  except:
    continue

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
    if conf.DEBUG:
      print("Пожар не попадает во временное окно - пропуск")
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

	# Фильтруем:
  if longitude_f>conf.bbox[0] and longitude_f < conf.bbox[2] and latitude_f > conf.bbox[1] and latitude_f < conf.bbox[3]:
    if conf.DEBUG:
      print("Ищем объекты близкие к координатам пожара %f,%f" %(longitude_f,latitude_f))
		
    for obj in get_near_object(corp_data_file,latitude_f,longitude_f):
      if conf.DEBUG:
        print("Вблизи объекта '%(name)s' происходит пожар. Расстояние до пожара: %(dist).0f метров. Ссылка на карту: http://map.prim.drsk.ru/#map=14/%(lat)f/%(lon)f&layer=MoFp" % {"name":obj["name"], "dist":obj["fire_distance"], "lat":obj["lat"],"lon":obj["lon"]})
      obj["fire_date"]=DateTime
      warning_list.append(obj)

# Записываем в выходной файл:
write_file(out_file,warning_list)
