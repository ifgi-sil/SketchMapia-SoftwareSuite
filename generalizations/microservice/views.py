from django.shortcuts import render
from django.template import loader
from django.http.response import HttpResponse
from django.views.decorators.http import require_POST
import osmnx as ox
import requests
import geopandas as gpd
from shapely.geometry import Polygon
from osmnx import utils
from osmnx import utils_graph
import numpy as np
from copy import deepcopy
import pandas as pd
import json
import os
import bcrypt
from shapely import geometry, ops
from shapely.geometry import Point, Polygon
from matplotlib import pyplot as plt
import shapely.wkt
from math import sqrt
import geojson
from geojson import Feature, Point, FeatureCollection, Polygon, dump
from django.http import JsonResponse


def routedirection(routedata,inputfile):
    # Network flow
    r_data = json.loads(str(routedata))
    nf_ids = set(data['id'] for data in r_data)
    f = open(inputfile)
    data_ip = json.load(f)
    ls=[]
    for feature in data_ip['features']:
        properties = feature['properties']
        id = properties.get('id')

        if id in nf_ids:
            geo = feature['geometry']
            coor = geo['coordinates']
            ls.append(coor)

    def joinSegments( s ):
        try:
            if s[0][0] == s[1][0] or s[0][0] == s[1][-1]:
                s[0].reverse()
            c = s[0][:]
            for x in s[1:]:
                if x[-1] == c[-1]:
                    x.reverse()
                c += x
            return c
        except IndexError:
            return []
    
    res = joinSegments(ls)
    
    def split_list(Input_list, n):
        for i in range(0, len(Input_list), n):
            yield Input_list[i:i + n]
    n = 2
    val=split_list(res, n)
    co_or=list(val)

    f_out=dict(zip(list(nf_ids), co_or))
    # print(f_out)
    return(f_out)

import logging

def requestFME(request):
    # if request.is_ajax() and request.method == 'POST':
    basedata = request.POST.get('basedata')
    sketchdata = request.POST.get('sketchdata')
    aligndata = request.POST.get('aligndata')
    routedata = request.POST.get('routedata')
    sketchroutedata= request.POST.get('sketchroutedata')
    
    USER_PROJ_DIR = "generalizedMap"
    baseMapdata = json.loads(basedata)
    sketchMapdata = json.loads(sketchdata)
    alignMapdata = json.loads(aligndata)
    
    try:
        # Get the directory of the current script
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Inputbasepath = os.path.join(current_dir, USER_PROJ_DIR, "inputbaseMap.json")
        # Inputsketchpath = os.path.join(current_dir, USER_PROJ_DIR, "inputsketchMap.json")
        # Inputaligndata = os.path.join(current_dir, USER_PROJ_DIR, "alignment.json")
        
        Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
        Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
        Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
        # breakpoint()
        if os.path.exists(Inputbasepath):
            os.remove(Inputbasepath)
        f = open(Inputbasepath, "a+")
        f.write(json.dumps(baseMapdata,indent=4))
        f.close()

        if os.path.exists(Inputsketchpath):
            os.remove(Inputsketchpath)
        f = open(Inputsketchpath, "a+")
        f.write(json.dumps(sketchMapdata,indent=4))
        f.close()

        if os.path.exists(Inputaligndata):
            os.remove(Inputaligndata)
        f = open(Inputaligndata, "a+")
        f.write(json.dumps(alignMapdata,indent=4))
        f.close()
    except IOError:
        print("Files written")
    
    result= spatial_transformation(routedata,sketchroutedata)

    return HttpResponse(result)


def spatial_transformation(routedata,sketchroutedata):
    USER_PROJ_DIR = "generalizedMap"
    # current_dir = os.path.dirname(os.path.abspath(__file__))
        
    # Inputbasepath = os.path.join(current_dir, USER_PROJ_DIR, "inputbaseMap.json")
    # Inputsketchpath = os.path.join(current_dir, USER_PROJ_DIR, "inputsketchMap.json")
    # Inputaligndata = os.path.join(current_dir, USER_PROJ_DIR, "alignment.json")
    Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
    Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
    Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
    
    base = open(Inputbasepath)
    sketch = open(Inputsketchpath)
    align = open(Inputaligndata)
    # breakpoint()
    # returns JSON object as a dictionary
    data = json.load(align)
    amal_ids = []
    ng_ids = []
    c_ids =[]
    om_ids=[]
    s_amal_ids = []
    # s_ng_ids = []
    s_c_ids =[]
    s_om_ids=[]
    for k,v in data.items():
        for val,val1 in v.items():
            key = 'genType'
            try:
                if val1[key] == 'Amalgamation':
                    id = val1['BaseAlign']['0']
                    amal_ids.append(id)
                    id1 = val1['SketchAlign']['0']
                    s_amal_ids.append(id1)
                if val1[key] == "No generalization":
                    ng_id = val1['BaseAlign']['0']
                    ng_ids.append(ng_id)
                    # ng_id1 = val1['SketchAlign']['0']
                    # s_ng_ids.append(ng_id1)

                if val1[key]== "OmissionMerge":
                    om_id = val1['BaseAlign']['0']
                    om_ids.append(om_id)
                    om_id1 = val1['SketchAlign']['0']
                    s_om_ids.append(om_id1)

                if val1[key]== "Collapse":
                    c_id = val1['BaseAlign']['0']
                    c_ids.append(c_id)
                    c_id1 = val1['SketchAlign']['0']
                    s_c_ids.append(c_id1)

            except (KeyError,TypeError) as error:
                continue

    data_ip = json.load(base)
    poly = []
    line = []
    point = []
    ng_ids_l = []
    ng_ids_p = []
    no_gen_l = []
    no_gen_p = []
    for i in data_ip['features']:
        geo = i['geometry']
        properties = i['properties']
        id = properties['id']
        for x in amal_ids:
            for y in x:
                if y == id :
                    type = geo['type']
                    coor = geo['coordinates']
                    f_coor = geometry.Polygon(coor[0])
                    poly.append(f_coor)
                else:
                    continue

        for x in om_ids:
            for y in x:
                if y == id :
                    type = geo['type']
                    coor = geo['coordinates']
                    f_coor = geometry.LineString(coor)
                    line.append(f_coor)
                else:
                    continue

        for x in ng_ids:
            for y in x:
                if y == id :
                    type = geo['type']
                    coor = geo['coordinates']
                    if len(coor) > 1:
                        # Create a LineString object
                        f_coor = geometry.LineString(coor)
                        no_gen_l.append(f_coor)
                        ng_ids_l.append(id)
                    else:
                        # Create a Polygon object
                        f_coor = geometry.Polygon(coor[0])
                        no_gen_p.append(f_coor)
                        ng_ids_p.append(id)
                else:
                    continue

        for x in c_ids:
            for y in x:
                if y == id :
                    type = geo['type']
                    coor = geo['coordinates']
                    f_coor = geometry.Polygon(coor[0])
                    point.append(f_coor)
                else:
                    continue
    
    poly_res = []
    for sublist in amal_ids:
        start = sum([len(sub) for sub in poly_res])
        end = start + len(sublist)
        poly_res.append(poly[start:end])

    point_res = []
    for sublist in c_ids:
        start = sum([len(sub) for sub in point_res])
        end = start + len(sublist)
        point_res.append(point[start:end])

    line_res = []
    for sublist in om_ids:
        start = sum([len(sub) for sub in line_res])
        end = start + len(sublist)
        line_res.append(line[start:end])
        
    ng_res_l = []
    for sublist in ng_ids:
        start = sum([len(sub) for sub in ng_res_l])
        end = start + len(sublist)
        ng_res_l.append(no_gen_l[start:end])
        
    ng_res_p = []
    for sublist in ng_ids:
        start = sum([len(sub) for sub in ng_res_p])
        end = start + len(sublist)
        ng_res_p.append(no_gen_p[start:end])
    
    s_ng_ids_l = []
    s_ng_ids_p = []
    
    # Iterate through the data and update SketchAlign
    for key, value in data.items():
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, dict) and "BaseAlign" in sub_value:
                base_align_value = sub_value["BaseAlign"]["0"][0]
                sketch_align_value = sub_value["SketchAlign"]["0"][0]
                
                if base_align_value in ng_ids_p:
                    s_ng_ids_p.append(sketch_align_value)
                elif base_align_value in ng_ids_l:
                    s_ng_ids_l.append(sketch_align_value)

    align.close()
    base.close()
    features = []
    
    # amalgamation 
    for x, ids, sids in zip(poly_res, amal_ids, s_amal_ids):
        mpt = geometry.MultiPolygon(x)
        res = mpt.convex_hull.wkt
        g1_a = shapely.wkt.loads(res)
        features.append(Feature(geometry=g1_a, properties={"genType": "Amalgamation", "BaseAlign": ids, "SketchAlign":sids[0]}))

    # omission_merge
    for x, ids, sids in zip(line_res, om_ids, s_om_ids):
        multi_line = geometry.MultiLineString(x)
        merged_line = ops.linemerge(multi_line)
        g1_o = shapely.wkt.loads(str(merged_line))
        features.append(Feature(geometry=g1_o, properties={"genType": "OmissionMerge", "BaseAlign": ids[0],"SketchAlign":sids[0]}))
   
    # collapse
    for x, ids, sids in zip(point_res, c_ids, s_c_ids):
        collapse = x[0].centroid
        g1_c = shapely.wkt.loads(str(collapse))
        features.append(Feature(geometry=g1_c, properties={"genType": "Collapse", "BaseAlign": ids[0],"SketchAlign":sids[0]}))
 
    # No Generalization
    for x, ids, sids in zip(ng_res_l, ng_ids_l, s_ng_ids_l):
        if len(x) == 0: # Skip empty inputs
            continue
        line = shapely.geometry.LineString(x[0])
        wkt_string = line.wkt
        features.append(Feature(geometry=shapely.wkt.loads(wkt_string), properties={"genType": "No generalization", "BaseAlign": ids,"SketchAlign":sids}))

    for x, ids, sids in zip(ng_res_p, ng_ids_p, s_ng_ids_p):
        if len(x) == 0: # Skip empty inputs
            continue
        polygon = shapely.geometry.Polygon(x[0])
        wkt_string = polygon.wkt
        features.append(Feature(geometry=shapely.wkt.loads(wkt_string), properties={"genType": "No generalization", "BaseAlign": ids,"SketchAlign":sids}))
          
    feature_collection = FeatureCollection(features)
    base = open(Inputbasepath)
    base_data = json.load(base)
    # Create a dictionary to map "id" to base data properties
    id_to_properties = {feature["properties"]["id"]: feature["properties"] for feature in base_data["features"]}
    
    # Iterate through feature collection features
    for feature in feature_collection["features"]:
        base_align = feature["properties"]["BaseAlign"]
        if isinstance(base_align, list):
            # Initialize an empty dictionary to store the merged properties
            merged_properties = {}

            # Loop through the list of IDs
            for bid in base_align:
                if bid in id_to_properties:
                    # Merge the properties of this ID into the merged_properties dictionary
                    merged_properties.update(id_to_properties[bid])

            # Update the feature's properties with the merged properties
            feature["properties"].update(merged_properties)
        elif base_align in id_to_properties:
            base_properties = id_to_properties[base_align]
            # Merge the sketch data properties into the feature collection properties
            feature["properties"].update(base_properties)

    f_out = routedirection(routedata,Inputbasepath)
    
    # Iterate through the features in inputbasemap and update coordinates if id matches
    for feature in feature_collection['features']:
        properties = feature['properties']
        id = properties.get("BaseAlign")
        # id = str(id_str).strip('[]')
        gen_type = properties.get('genType')
        if gen_type == "No generalization" and id in f_out :
            geo = feature['geometry']
            geo['coordinates'] = f_out[id]
    
    for feature in feature_collection['features']:
        # Check if the geometry type is 'Point'
        type = feature['geometry']['type']
        # coordinates = feature['geometry']['coordinates']
        if type == 'Point':
            # Create a GeoDataFrame with the input feature
            gdf = gpd.GeoDataFrame.from_features([feature])

            # Set the coordinate reference system (CRS) to a standard one, e.g., EPSG:4326
            gdf.crs = "EPSG:4326"

            # Create a buffered polygon around the point (e.g., with a radius of 1 unit)
            buffered_radius = 1.0
            buffered_polygon = gdf.buffer(buffered_radius)

            # Simplify the buffered polygon to reduce the number of coordinates
            simplified_buffer = buffered_polygon.simplify(0.001)
            
            # Convert the simplified buffered polygon to GeoJSON format
            simplified_geojson = simplified_buffer.to_json()
            
            # Parse the simplified GeoJSON string to a Python dictionary
            simplified_data = json.loads(simplified_geojson)
            
            # Update the 'geometry' key in the original feature
            feature['geometry'] = simplified_data['features'][0]['geometry']

    
    sketchroute= routedirection(sketchroutedata,Inputsketchpath)

    sketch = open(Inputsketchpath)
    sketchdata= json.load(sketch)
    for feature in sketchdata['features']:
        properties = feature['properties']
        id = properties.get('id')
        if id in sketchroute:
            geo = feature['geometry']
            geo['coordinates'] = sketchroute[id]
            
    for feature in sketchdata['features']:
        # Check if the geometry type is 'Point'
        type = feature['geometry']['type']
        feature['properties']['mapType'] = 'Sketch'
        # coordinates = feature['geometry']['coordinates']
        if type == 'Point':
            # Create a GeoDataFrame with the input feature
            gdf = gpd.GeoDataFrame.from_features([feature])

            # Set the coordinate reference system (CRS) to a standard one, e.g., EPSG:4326
            gdf.crs = "EPSG:4326"

            # Create a buffered polygon around the point (e.g., with a radius of 1 unit)
            buffered_radius = 1.0
            buffered_polygon = gdf.buffer(buffered_radius)

            # Simplify the buffered polygon to reduce the number of coordinates
            simplified_buffer = buffered_polygon.simplify(0.001)
            
            # Convert the simplified buffered polygon to GeoJSON format
            simplified_geojson = simplified_buffer.to_json()
            
            # Parse the simplified GeoJSON string to a Python dictionary
            simplified_data = json.loads(simplified_geojson)
            
            # Update the 'geometry' key in the original feature
            feature['geometry'] = simplified_data['features'][0]['geometry']
            
    # Assuming you have two feature collections, feature_collection1 and feature_collection2
    combined_feature_collection = {
        "type": "FeatureCollection",
        "features": []
    }
    # Append the features from feature_collection1 to the combined feature collection
    for feature in feature_collection["features"]:
        combined_feature_collection["features"].append(feature)

    # Append the features from feature_collection2 to the combined feature collection
    for feature in sketchdata["features"]:
        combined_feature_collection["features"].append(feature)
        
    # breakpoint()
    print(combined_feature_collection)

    outputpath =  os.path.join(USER_PROJ_DIR,"generalizedoutputMap"+".json")
    if os.path.exists(outputpath):
        os.remove(outputpath)
    f = open(outputpath, "a+")
    f.write(json.dumps(combined_feature_collection,indent=4))
    f.close()
    
    return(json.dumps(combined_feature_collection,indent=4))




