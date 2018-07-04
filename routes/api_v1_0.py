from flask import Flask, render_template, Blueprint, Response, request, redirect, send_file, send_from_directory, jsonify
from flask_babel import gettext, format_date
import json
import datetime
from io import BytesIO
from PIL import Image
import io
from oceannavigator.dataset_config import (
    get_variable_name, get_datasets,
    get_dataset_url, get_dataset_climatology, get_variable_scale,
    is_variable_hidden, get_dataset_cache, get_dataset_help,
    get_dataset_name, get_dataset_quantum, get_dataset_attribution
)
from utils.errors import ErrorBase, ClientError, APIError
import utils.misc

from plotting.transect import TransectPlotter
from plotting.drifter import DrifterPlotter
from plotting.map import MapPlotter
from plotting.timeseries import TimeseriesPlotter
from plotting.ts import TemperatureSalinityPlotter
from plotting.sound import SoundSpeedPlotter
from plotting.profile import ProfilePlotter
from plotting.hovmoller import HovmollerPlotter
from plotting.observation import ObservationPlotter
from plotting.class4 import Class4Plotter
from plotting.stick import StickPlotter
from plotting.stats import stats as areastats
import plotting.colormap
import plotting.tile
import plotting.scale
import numpy as np
import re
import os
import netCDF4
import base64
import pytz
from data import open_dataset
from data.netcdf_data import NetCDFData
import routes.routes_impl

bp_v1_0 = Blueprint('api_v1_0', __name__) # Creates the blueprint for api queries

#~~~~~~~~~~~~~~~~~~~~~~~
# API INTERFACE 
#~~~~~~~~~~~~~~~~~~~~~~~

@bp_v1_0.route("/api/v1.0/generatescript/<string:url>/<string:type>/")
def generateScript(url, type):
  print("URL: " + url)
  url = json.loads(url)
  print("JSON LOADS URL: ")
  print(url)

  if type == "python":
    #setup file
    #script = io.BytesIO()
    script = io.StringIO()

    #FILE CONTENTS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #HEADER---------------------

    script.write("from urllib.request import urlopen\n")
    script.write("from urllib.parse import urlencode\n")
    script.write("from contextlib import closing\n")
    script.write("from PIL import Image\n")
    script.write("import json\n")
    script.write("\n\n")

    #Set Navigators URL
    script.write("#Set Navigator URL\n")
    script.write('base_url = "http://navigator.oceansdata.ca/plot/?"\n\n')

    #---------------------------

    #CREATE JSON OBJECT---------

    script.write("#Create JSON Object\n")
    script.write("query = {\n")
    for x in url:
      print(x)
      #print(type(url.get(x)))
      if isinstance(url.get(x), str):
        script.write('  "' + x + '": "' + str(url.get(x)) + '"' + ",\n" )
      else:
        script.write('  "' + x + '": ' + str(url.get(x)) + ",\n")
      print(url.get(x))
    script.write("}\n")
    #---------------------------



    #Assemble full request
    script.write('\n#Assemble full request - converts json object to url\n')
    script.write("url = base_url + urlencode(" + '{"query": ' + "json.dumps(query)})" + "\n")
    script.write("print(url)")



    #Open URL and read response
    script.write("\n#Open URL and save response\n")
    script.write("with closing(urlopen(url)) as f:\n")
    script.write("  img = Image.open(f)\n")
    script.write('  img.save("script_template_" + str(query["dataset"]) + "_" + str(query["time"]) + ".png" , "PNG")\n')


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #CONVERT TO BytesIO TO SEND
    b = io.BytesIO()
    script.seek(0)
    b.write(bytes(script.read(),'utf-8'))
    b.seek(0)
    print("B: ")
    print(b.read())
    b.seek(0)

  elif type == "r":
    return json.dumps("Under Construction")
  
  resp = send_file(b, as_attachment=True, attachment_filename='script_template.py', mimetype='application/x-python')
  return resp

#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/datasets/')
def query_datasets_v1_0():
  return routes.routes_impl.query_datasets_impl(request.args)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/variables/')
def vars_query_v1_0():
  return routes.routes_impl.vars_query_impl(request.args)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/observationvariables/')
def obs_vars_query_v1():
  return routes.routes_impl.obs_vars_query_impl()


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/timestamps/')
def time_query_v1_0():
  return routes.routes_impl.time_query_impl(request.args)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/depth/')
def depth_v1():
  return routes.routes_impl.depth_impl(request.args)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/scale/<string:dataset>/<string:variable>/<string:scale>.png')
def scale_v1_0(dataset, variable, scale):
  return routes.routes_impl.scale_impl(dataset, variable, scale)


#
# Change to timestamp from v0.0
#
@bp_v1_0.route('/api/v1.0/range/<string:dataset>/<string:variable>/<string:interp>/<int:radius>/<int:neighbours>/<string:projection>/<string:extent>/<string:depth>/<string:time>.json')
def range_query_v1_0(dataset, variable, interp, radius, neighbours, projection, extent, depth, time):
  with open_dataset(get_dataset_url(dataset)) as ds:
    date = ds.convert_to_timestamp(time)
    return routes.routes_impl.range_query_impl(interp, radius, neighbours, dataset, projection, extent, variable, depth, date)


# Changes from v0.0:
# ~ Added timestamp conversion
# 
@bp_v1_0.route('/api/v1.0/data/<string:dataset>/<string:variable>/<string:time>/<string:depth>/<string:location>.json')
def get_data_v1_0(dataset, variable, time, depth, location):
  with open_dataset(get_dataset_url(dataset)) as ds:
    date = ds.convert_to_timestamp(time)
    print(date)
    return routes.routes_impl.get_data_impl(dataset, variable, date, depth, location)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/class4/<string:q>/<string:class4_id>/')
def class4_query_v1_0(q, class4_id):
    return routes.routes_impl.class4_query_impl(q, class4_id, 0)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/drifters/<string:q>/<string:drifter_id>')
def drifter_query_v1_0(q, drifter_id):
  return routes.routes_impl.drifter_query_impl(q, drifter_id)


#
# Change to timestamp from v0.0
#
@bp_v1_0.route('/api/v1.0/stats/', methods=['GET', 'POST'])
def stats_v1_0():

  if request.method == 'GET':
    args = request.args
  else:
    args = request.form
  query = json.loads(args.get('query'))

  with open_dataset(get_dataset_url(query.get('dataset'))) as dataset:
    date = dataset.convert_to_timestamp(query.get('time'))
    date = {'time' : date}
    query.update(date)

    return routes.routes_impl.stats_impl(args, query)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/subset/')
def subset_query_v1_0():
    return routes.routes_impl.subset_query_impl(request.args)


#
# Change to timestamp from v0.0
#
@bp_v1_0.route('/api/v1.0/plot/', methods=['GET', 'POST'])
def plot_v1_0():

  if request.method == 'GET':
    args = request.args
  else:
    args = request.form
  query = json.loads(args.get('query'))

  with open_dataset(get_dataset_url(query.get('dataset'))) as dataset:
    date = dataset.convert_to_timestamp(query.get('time'))
    date = {'time' : date}
    query.update(date)

    return routes.routes_impl.plot_impl(args, query)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/colors/')
def colors_v1_0():
  return routes.routes_impl.colors_impl(request.args)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/colormaps/')
def colormaps_v1_0():
  return routes.routes_impl.colormaps_impl()


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/colormaps.png')
def colormap_image_v1_0():
  return routes.routes_impl.colormap_image_impl()


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/')
def info_v1_0():
  return routes.routes_impl.info_impl()


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/<string:q>/')
def query_v1_0(q):
  return routes.routes_impl.query_impl(q)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/<string:q>/<string:q_id>.json')
def query_id_v1_0(q, q_id):
  return routes.routes_impl.query_id_impl(q, q_id)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/<string:q>/<stringLprojection>/<int:resolution>/<string:extent>/<string:file_id>.json')
def query_file_v1_0(q, projection, resolution, extent, file_id):
  return routes.routes_impl.query_file_impl(q, projection, resolution, extent, file_id)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/timestamp/<string:old_dataset>/<int:date>/<string:new_dataset>')
def timestamp_for_date_v1_0(old_dataset, date, new_dataset):
  return routes.routes_impl.timestamp_for_date_impl(old_dataset, date, new_dataset)


#
# Change to timestamp from v0.0
#
@bp_v1_0.route('/api/v1.0/tiles/<string:interp>/<int:radius>/<int:neighbours>/<string:projection>/<string:dataset>/<string:variable>/<string:time>/<string:depth>/<string:scale>/<int:zoom>/<int:x>/<int:y>.png')
def tile_v1_0(projection, interp, radius, neighbours, dataset, variable, time, depth, scale, zoom, x, y):
  with open_dataset(get_dataset_url(dataset)) as ds:
    date = ds.convert_to_timestamp(time)
    return routes.routes_impl.tile_impl(projection, interp, radius, neighbours, dataset, variable, date, depth, scale, zoom, x, y)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/tiles/topo/<string:projection>/<int:zoom>/<int:x>/<int:y>.png')
def topo_v1_0(projection, zoom, x, y):
  return routes.routes_impl.topo_impl(projection, zoom, x, y)


#
# Unchanged from v0.0
#
@bp_v1_0.route('/api/v1.0/tiles/bath/<string:projection>/<int:zoom>/<int:x>/<int:y>.png')
def bathymetry_v1_0(projection, zoom, x, y):
  return routes.routes_impl.bathymetry_impl(projection, zoom, x, y)

