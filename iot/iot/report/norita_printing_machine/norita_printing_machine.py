# Copyright (c) 2013, JETFOX - PT.Perkasa Jaya Kirana and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, time
from datetime import datetime, timedelta, date
import collections
from elasticsearch import Elasticsearch
from random import randint
from frappe.utils import getdate, cstr, flt
from frappe.utils import (convert_utc_to_user_timezone, now)

def execute(filters=None):
	columns, data = ['Date','Shift 1', 'Shift 2', 'Shift 3'], []
	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)

	label, data = get_data2(from_date, to_date, filters.node, filters.signal)

	return columns, data

def get_data(from_date, to_date, node, signal):
	site_name = cstr(frappe.local.site)
	es = Elasticsearch([frappe.get_conf().get("elastic_norita_server")],scheme="https", port=443)
	doc = {"size":0,"aggs":{"machine_performance":{"date_histogram":{"field":"id","interval":"8h","format":"yy-MM-dd HH:mm","time_zone":"+07:00","offset":"+0h"},"aggs":{"max_output1":{"max":{"field":"192_168_1_128.PM1_Line_Speed"}}}}}}
	res = es.search(index=site_name, body=doc)
	res = res['aggregations']['machine_performance']['buckets']
	wss = frappe.get_doc("Work Shift Settings")

	label, data = [], []
	for r in res:
		t = time.localtime(r['key'])
		l = "{}-{}-{}".format(t.tm_mday, t.tm_mon, t.tm_year)
		if r['max_output1']['value'] == None:
			continue
		label.append(r['key_as_string'])
		data.append([r['key_as_string'], int(r['max_output1']['value']), int(r['max_output2']['value'])])
		# if t.hour == t_end_shift1.hour and abs(t.minute - t_end_shift1.minute) < 2:
        # 	data.append([r['key_as_string'], r['max_output1']['value'], r['max_output2']['value'],])
		# elif t.hour == t_end_shift2.hour and abs(t.minute - t_end_shift2.minute) < 2:

		# elif t.hour == t_end_shift3.hour and abs(t.minute - t_end_shift3.minute) < 2:
	print(data)
	return label, data

def get_data2(from_date, to_date, node, signal):
	es = Elasticsearch([frappe.get_conf().get("elastic_norita_server")],scheme="https", port=443)
	doc = {"size":0,"query":{"constant_score":{"filter":{"range":{"id":{"gte":from_date,"lte":to_date,"format":"yyyy-MM-dd","time_zone":"+07:00"}}}}},"aggs":{"machine_performance":{"date_histogram":{"field":"id","interval":"8h","format":"yy-MM-dd HH:mm","time_zone":"+07:00","offset":"+0h"},"aggs":{"max_output1":{"max":{"field":"192_168_1_128.PM1_Line_Speed"}}}}}}
	res = es.search(index="norita", body=doc)
	res = res['aggregations']['machine_performance']['buckets']
	wss = frappe.get_doc("Work Shift Settings")

	print(res)

	t_end_shift1 = datetime.strptime(wss.shift_1_end, "%H:%M:%S").time()
	t_end_shift2 = datetime.strptime(wss.shift_2_end, "%H:%M:%S").time()
	t_end_shift3 = datetime.strptime(wss.shift_3_end, "%H:%M:%S").time()

	label, data, d = [], [], {}

	for r in res:
		if r['max_output1']['value'] == None:
			continue

		utc_dt = datetime.utcfromtimestamp(r['key']/1000 - 1)
		t = convert_utc_to_user_timezone(utc_dt)
		date_str = t.strftime('%y-%m-%d')

		if date_str not in d:
			d[date_str] = [0, 0, 0]

		if get_time_delta(t.time(), t_end_shift1) < 2 : #and (t_old.tm_mon != t.tm_mon or t_old.tm_mday != t.tm_mday or t_old.tm_year != t.tm_year)
			d[date_str][0] = int(r['max_output1']['value'])
			# print('shift 1: ' +  str(r['max_output1']['value']))
		elif get_time_delta(t.time(), t_end_shift2) < 2:
			d[date_str][1] = int(r['max_output1']['value'])
			# print('shift 2: ' +  str(r['max_output1']['value']))
		elif get_time_delta(t.time(), t_end_shift3) > 86280 or get_time_delta(t.time(), t_end_shift3) < 2: # 86280 = 23 hours*3600 + 58 min* 60
			if date_str not in d:
				d[date_str] = [0, 0, 0]
			d[date_str][2] = int(r['max_output1']['value'])
			print('shift 3: ' +  str(r['max_output1']['value']))

	od = collections.OrderedDict(sorted(d.items()))

	data = [[k]+v for k, v in od.items()]

	return label, data

def get_time_delta(t0, t1):
	return abs((datetime.combine(date.today(),t0) - datetime.combine(date.today(),t1)).total_seconds())