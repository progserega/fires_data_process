#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi
import os
import time
import sys

stand_alone_page=True
if len(sys.argv) > 1:
	if sys.argv[1] == "noheader":
		stand_alone_page=False

if not stand_alone_page:
	print("""
<HEAD>
<STYLE TYPE="text/css">
<!--
@page { size: 21cm 29.7cm; margin: 2cm }
P { margin-bottom: 0.21cm }
-->
</STYLE>

<style>
   .normaltext {
   }
</style>
<style>
   .ele_null {
    color: red; /* Красный цвет выделения */
   }
</style>
<style>
   .green {
    color: green; /* Зелёный цвет выделения */
	background: #D9FFAD;
	font-size: 100%;
   }
</style>

</HEAD>
<BODY LANG="ru-RU" LINK="#000080" VLINK="#800000" DIR="LTR">
""")
else:
	print("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
<TITLE>Пожары</TITLE>
<META NAME="GENERATOR" CONTENT="OpenOffice.org 3.1  (Linux)">
<META NAME="AUTHOR" CONTENT="Сергей Семёнов">
<META NAME="CREATED" CONTENT="20100319;10431100">
<META NAME="CHANGEDBY" CONTENT="Сергей Семёнов">
<META NAME="CHANGED" CONTENT="20100319;10441400">
<meta http-equiv="Refresh" content="60" />
<link rel="shortcut icon" href="favicon_fire.png" type="image/png">
<STYLE TYPE="text/css">
<!--
@page { size: 21cm 29.7cm; margin: 2cm }
P { margin-bottom: 0.21cm }
-->
</STYLE>

<style>
   .normaltext {
   }
</style>
<style>
   .ele_null {
    color: red; /* Красный цвет выделения */
   }
</style>
<style>
   .green {
    color: green; /* Зелёный цвет выделения */
	background: #D9FFAD;
	font-size: 100%;
   }
</style>

</HEAD>
<BODY LANG="ru-RU" LINK="#000080" VLINK="#800000" DIR="LTR">
""")

station_warning_list="/var/osm/fires//station_warning_list.csv"
tp_warning_list="/var/osm/fires//tp_warning_list.csv"

mod_time_station=time.strftime("%d.%m.%Y %H:%M", time.localtime(os.stat(station_warning_list).st_mtime) )
mod_time_tp=time.strftime("%d.%m.%Y %H:%M", time.localtime(os.stat(tp_warning_list).st_mtime) )

print("""
<h2>Список объектов ОАО ДРСК, вблизи которых зафиксированы возгорания</h2>
Данные о пожарах обновляются каждые 4 часа. В данный список попадают объекты, вблизи которых (ближе 2000 метров) за последние 24 часа были зафиксированы пожары разной степени серьёзности. <br><br>""")

print("""
		<TABLE BORDER>
		<TR>    
				<TH COLSPAN=5>Список подстанций, рядом с которыми зафиксированны пожары
				<br> Последнее обновление данных о пожарах в %s</TH>
		</TR>
		<TR>
				<TH COLSPAN=1>№</TH>
				<TH COLSPAN=1>Имя подстанции</TH>
				<TH COLSPAN=1>Расстояние до пожара (метры)</TH>
				<TH COLSPAN=1>Дата/время обнаружения пожара</TH>
				<TH COLSPAN=1>Ссылка на карту</TH>
		</TR>
		""" % mod_time_station)

if os.stat(station_warning_list).st_size > 0:
	index=0
	for line in open(station_warning_list):
		name,lon,lat,dist,date=line.split("|")
		index+=1
		print("""<TR>
			 <TD>%(index)d</TD>
			 <TD>%(name)s</TD>
			 <TD>%(dist).0f</TD>
			 <TD>%(date)s</TD>
			 <TD><a target="_self" href="http://map.prim.drsk.ru/#map=14/%(lat)s/%(lon)s&layer=MoFp">карта</a></TD>
			 </TR>""" % {"index":index, "name":name, "dist":float(dist), "lat":lat, "lon":lon, "date":date})
else:
	print ("""<TD COLSPAN=5>
	<p align="center">
	<span class="green">
	Рядом с подстанциями пожары не обнаружены
	</span>
	</p>
	</TD>""")
	

print("</TABLE><br><br>")


print("""
		<TABLE BORDER>
		<TR>    
				<TH COLSPAN=5>Список ТП/ЗТП/КТП, рядом с которыми зафиксированны пожары 
				<br> Последнее обновление данных о пожарах в %s</TH>
		</TR>
		<TR>
				<TH COLSPAN=1>№</TH>
				<TH COLSPAN=1>Имя ТП/КТП/ЗТП</TH>
				<TH COLSPAN=1>Расстояние до пожара (метры)</TH>
				<TH COLSPAN=1>Дата/время обнаружения пожара</TH>
				<TH COLSPAN=1>Ссылка на карту</TH>
		</TR>
		""" % mod_time_tp)

if os.stat(tp_warning_list).st_size > 0:
	index=0
	for line in open(tp_warning_list):
		name,lon,lat,dist,date=line.split("|")
		index+=1
		print("""<TR>
			 <TD>%(index)d</TD>
			 <TD>%(name)s</TD>
			 <TD>%(dist).0f</TD>
			 <TD>%(date)s</TD>
			 <TD><a target="_self" href="http://map.prim.drsk.ru/#map=14/%(lat)s/%(lon)s&layer=MoFp">карта</a></TD>
			 </TR>""" % {"index":index, "name":name, "dist":float(dist), "lat":lat, "lon":lon, "date":date})
else:
	print ("""<TD COLSPAN=5>
	<p align="center">
	<span class="green">
	Рядом с ТП/ЗТП/КТП пожары не обнаружены
	</span>
	</p>
	</TD>""")

print("</TABLE>")
print ("""
<p align="left">
Страница автоматически обновляется раз в минуту.
</p>""")

print("""
</body>
""")
if stand_alone_page:
	print("""
</html>
""")
