#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-

import urllib
#import httplib
import sys
import os
import psycopg2
import psycopg2.extras
import db_config as config
import math
import tempfile

def get_node_info(node_id):
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select latitude,longitude from nodes where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id=%(node_id)d limit 1""" % {"node_id":node_id} )
		cur.execute("""select latitude,longitude from nodes where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id=%(node_id)d limit 1""" % {"node_id":node_id} )
		data = cur.fetchone()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	node={}
	node["lat"]=((float) (data[0]) )/10000000
	node["lon"]=((float) (data[1]) )/10000000
	node["id"]=node_id
	node["map_url"]="http://map.prim.drsk.ru/#map=17/%(lat)f/%(lon)f&layer=Mo&poi=Ia1" % {"lat":node["lat"], "lon":node["lon"]}
	return node

def get_node_by_way(way_id):
	node_id=-1
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select node_id from way_nodes where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id=%(way_id)d limit 1""" % {"way_id":way_id } )
		cur.execute("""select node_id from way_nodes where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id=%(way_id)d limit 1""" % {"way_id":way_id } )
		node_id=cur.fetchone()[0]
	except:
		print ("I am unable fetch data from db (41)");sys.exit(1)
	if node_id==-1:
		print ("way_id=%d not have nodes!" % way_id);sys.exit(1)
	return node_id

def get_station_as_nodes(power_stations):
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select node_id,v from node_tags where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id in (select node_id from node_tags where (k='power' and v='station')) and k='name'""" )
		cur.execute("""select node_id,v from node_tags where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id in (select node_id from node_tags where (k='power' and v='station')) and k='name'""" )
		# Загоняем значения в set(), преобразуя из списка, т.к. в set() будут только уникальные значения:
		nodes = cur.fetchall()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	for node in nodes:
		station={}
		station["station_name"]=node[1]
		station["node"]=get_node_info(node[0])
		# Добавляем данные о линии только если такой линии там нет (она могла быть добавлена как отношение):
		if not station["station_name"] in power_stations:
			power_stations[station["station_name"]]=station
	return power_stations

def get_station_as_ways(power_stations):
	try:
		# Берём список идентификаторов линий и наименований этих линий, которым принадлежит эта точка:
		if config.debug==True:
			print("""select way_id,v from way_tags where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id in (select way_id from way_tags where (k='power' and v='station')) and k='name'""" )
		cur.execute("""select way_id,v from way_tags where cast(way_id as text) || '-' || cast(version as text) in ( select cast(way_id as text) || '-' || cast(max(version) as text) as tt from ways group by way_id) and way_id in (select way_id from way_tags where (k='power' and v='station')) and k='name'""" )
		ways = cur.fetchall()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	for way in ways:
		station={}
		station["way_id"]=way[0]
		station["node"]=get_node_info(get_node_by_way(way[0]))
		station["station_name"]=way[1]
		# берём первую точку в линии и по ней определяем координаты и т.п. информацию:

		# Добавляем данные о линии только если такой линии там нет (она могла быть добавлена как отношение):
		if not station["station_name"] in power_stations:
			power_stations[station["station_name"]]=station
	return power_stations


def write_power_stations(file_name, power_stations):
	f=open(file_name,"w+")
	for station_name in power_stations:
		station=power_stations[station_name]
		#data=u"""|%(lon)f|%(lat)f|%(name)s|\n""" % {"lon":station["node"]["lon"],"lat":station["node"]["lat"], "name":station_name.encode('utf-8') } 
		data="""%(lon)f|%(lat)f|%(name)s\n""" % {"lon":station["node"]["lon"],"lat":station["node"]["lat"], "name":station_name } 
		if config.debug:
			#print(u"write data: %s" % data)
			print("write data: %s" % data)
		#f.write(data.encode("utf-8"))
		f.write(data)
	f.close()

# ======================================= main() ===========================

if len(sys.argv) < 2:
	print("Необходим один параметр - имя файла, куда будет сохраняться список подстанций\n")
	sys.exit(1)

out_file=sys.argv[1]

try:
	if config.debug:
		print("connect to: dbname='" + config.db_name + "' user='" +config.db_user + "' host='" + config.db_host + "' password='" + config.db_passwd + "'")
	conn = psycopg2.connect("dbname='" + config.db_name + "' user='" +config.db_user + "' host='" + config.db_host + "' password='" + config.db_passwd + "'")
	cur = conn.cursor()
except:
    print ("I am unable to connect to the database");sys.exit(1)

power_stations={}

# Берём все Подстанции как линии:

# Добавляем простые линии, если их не добавили как отношения:
get_station_as_ways(power_stations)
get_station_as_nodes(power_stations)

# Записываем список подстанций:
write_power_stations(out_file, power_stations)
sys.exit(0)
