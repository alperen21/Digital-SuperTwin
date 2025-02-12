from influxdb import InfluxDBClient
from influxdb import SeriesHelper

import pandas as pd
from datetime import datetime
import time

import sys
sys.path.append("../")

import utils

def query_string(metric, tagkey):
  
  return 'SELECT * FROM ' + metric + ' where "tag"'+ "=" +  "'" + tagkey + "'"

def difference(to_normal, normal):
    
  t0 = int(time.mktime(time.strptime(to_normal, "%Y-%m-%dT%H:%M:%S.%fZ")))
  t1 = int(time.mktime(time.strptime(normal, "%Y-%m-%dT%H:%M:%S.%fZ")))

  return (t1 - t0) * -1
  
def normalized(to_normal, difference): ##Other observation, vs. itself

  t0 = int(time.mktime(time.strptime(to_normal, "%Y-%m-%dT%H:%M:%S.%fZ")))
  t0 -= difference
  t0 = datetime.fromtimestamp(t0)
  t0 = str(t0)
  
  return t0.split(" ")[0] + "T" + t0.split(" ")[1] + ".000000Z"

def normalize_tag(SuperTwin, _tag, no_subtags):
  
  db = utils.get_influx_database(SuperTwin.influxdb_addr, SuperTwin.influxdb_name)
  db.switch_database(SuperTwin.influxdb_name)
  
  ###Zeroth settings
  zero_tagkey = _tag + "_0"
  metrics = SuperTwin.observation_metrics
  metrics = [x.strip(" node") for x in metrics]
  metrics = ["perfevent_hwcounters_" + x.replace(":", "_") + "_value" for x in metrics]
    
  zero_query_string = query_string(metrics[0], zero_tagkey)
  result = db.query(zero_query_string)
  result = list(result)[0]
  compare_time = result[0]["time"]
  ###Zeroth settings
  
    
  ##Setback all sets
  for i in range(no_subtags):
    tagkey = _tag + "_" + str(i)
    for metric in metrics:
      
      qs = query_string(metric, tagkey)
      print("Normalize measurement time:", qs)
      result = list(db.query(qs))[0]
      my_difference = difference(result[0]['time'], compare_time)
      my_write = []
      ##Need to write ALL points
      
      for i in range(len(result)):
        time = ""
        if(tagkey.find("_0") != -1):
          n_time = result[i]['time']
        else:
          n_time = normalized(result[i]['time'], my_difference)
          
          to_write = {"measurement": metric,
                      "tags": {"tag": tagkey + "_normalized"},
                      "time": n_time}
          to_write["fields"] = {}
          for key in result[i].keys():
            if(key != "tag" and key != "time"):
              to_write["fields"][key] = result[i][key]
              my_write.append(to_write)
          db.write_points(my_write)
    
            

def normalize_twin_tags(st1, st2, st3, st4):

  twin1 = st1[0]
  twin1_tag = st1[1]

  
  twin2 = st1[0]
  twin2_tag = st1[1]

  
  twin3 = st1[0]
  twin3_tag = st1[1]

  
  twin4 = st1[0]
  twin4_tag = st1[1]

  
  db = utils.get_influx_database(twin1.influxdb_addr, twin1.influxdb_name)
  db.switch_database(twin1.influxdb_name)
  
  ###Zeroth settings
  metrics = twin1.observation_metrics
  metrics = [x.strip(" node") for x in metrics]
  metrics = ["perfevent_hwcounters_" + x.replace(":", "_") + "_value" for x in metrics]
    
  zero_query_string = query_string(metrics[0], twin1_tag)
  result = db.query(zero_query_string)
  result = list(result)[0]
  compare_time = result[0]["time"]
  ###Zeroth settings
  

  sts = [st1,st2,st3,st4]
    ##Setback all sets
  for i in range(0,4):
    twin = sts[i][0]
    tagkey = sts[i][1]
    db = utils.get_influx_database(twin.influxdb_addr, twin.influxdb_name)
    db.switch_database(twin.influxdb_name)
    print("Switched to:", twin.influxdb_name)
    ###Get metrics for all
    metrics = twin.observation_metrics
    metrics = [x.strip(" node") for x in metrics]
    metrics = ["perfevent_hwcounters_" + x.replace(":", "_") + "_value" for x in metrics]
    ###Get metrics for all
    for metric in metrics:
      
      qs = query_string(metric, tagkey)
      print("Normalize measurement time:", qs, "on ", twin.name)
      result = list(db.query(qs))[0]
      my_difference = difference(result[0]['time'], compare_time)
      my_write = []
            ##Need to write ALL points
            
      for i in range(len(result)):
        time = ""
        if(tagkey.find("_0") != -1):
          n_time = result[i]['time']
        else:
          n_time = normalized(result[i]['time'], my_difference)
          
          to_write = {"measurement": metric,
                      "tags": {"tag": tagkey + "_normalized"},
                      "time": n_time}
          to_write["fields"] = {}
          for key in result[i].keys():
            if(key != "tag" and key != "time"):
              to_write["fields"][key] = result[i][key]
              my_write.append(to_write)
      db.write_points(my_write)
        #print("Writing:", my_write)
