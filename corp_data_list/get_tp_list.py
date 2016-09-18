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

def deg2grad_min_sec(deg):
	# Получаем целую часть:
	#grad=math.fabs(deg)
	# все способы сокращают до целого, в большую сторону, а на нам нужно именно точно:
	grad=int(("%f" % deg).split(".")[0])
	ost=deg-grad
	minutes=int(("%f" % (ost*60)).split(".")[0])
	ost=ost*60-minutes
	sec=ost*60
	return """%d°%d'%.2f" """ % (grad,minutes,sec)


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
	# Вычисляем градусы, минуты, секунды:
	node["lat_grad_min_sec"]=deg2grad_min_sec(node["lat"])
	node["lon_grad_min_sec"]=deg2grad_min_sec(node["lon"])

	node["id"]=node_id
	node["map_url"]="http://map.prim.drsk.ru/#map=17/%(lat)f/%(lon)f&layer=Mp&poi=Ka1" % {"lat":node["lat"], "lon":node["lon"]}
	return node

def get_tp_as_nodes(power_tp):
	try:
		# Берём список идентификаторов точек, которым присвоены теги подстанций:
		if config.debug==True:
			print("""select node_id,v from node_tags where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id in (select node_id from node_tags where (k='power' and v='sub_station')) and k='ref'""" )
		cur.execute("""select node_id,v from node_tags where cast(node_id as text) || '-' || cast(version as text) in ( select cast(node_id as text) || '-' || cast(max(version) as text) as tt from nodes group by node_id) and node_id in (select node_id from node_tags where (k='power' and v='sub_station')) and k='ref'""" )
		# Загоняем значения в set(), преобразуя из списка, т.к. в set() будут только уникальные значения:
		nodes = cur.fetchall()
	except:
		print ("I am unable fetch data from db");sys.exit(1)
	if config.debug:
		print("получено подстанций: %d" % len(nodes))
	for node in nodes:
		tp={}
		tp["node_id"]=node[0]
		tp["tp_name"]=node[1]
		tp["node"]=get_node_info(node[0])
		# Добавляем данные о тп только если такой тп там нет (по id, а не по имени, т.к. имена могут совпадать в разных РЭС)
		if not tp["node_id"] in power_tp:
			power_tp[tp["node_id"]]=tp
	return power_tp



def write_power_tp(file_name, power_tp):
	f=open(file_name,"w+")
	for tp_node_id in power_tp:
		tp=power_tp[tp_node_id]
		#data=u"""|%(lon)f|%(lat)f|%(name)s|\n""" % {"lon":tp["node"]["lon"],"lat":tp["node"]["lat"], "name":tp_name.encode('utf-8') } 
		data="""%(lon)f|%(lat)f|%(name)s\n""" % {"lon":tp["node"]["lon"],"lat":tp["node"]["lat"], "name":tp["tp_name"] } 
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

power_tp={}

# Берём все ТП:

get_tp_as_nodes(power_tp)

# Записываем список подстанций:
write_power_tp(out_file, power_tp)
sys.exit(0)
