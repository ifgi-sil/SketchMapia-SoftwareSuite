from django.shortcuts import render

# Create your views here.
from django.template import loader
from django.http.response import HttpResponse
import osmnx as ox
import requests
import geopandas as gpd
from shapely.geometry import Polygon
from osmnx import utils
from osmnx import utils_graph
import numpy as np
from analyser import completeness
from analyser import qualitativeAnalyser
from qualifier import qualify_map
from copy import deepcopy
import pandas as pd
from analyser import inverses
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

global G


def map(request):
    template = loader.get_template('../templates/generalizingmaps.html')
    return HttpResponse(template.render({}, request))


def fetch_data(request):
    template = loader.get_template('../templates/generalizingmaps.html')
    if request.is_ajax():
        # extract your params
        latlng_array =[]
        for i, j in request.POST.items():
            latlng = request.POST.getlist(i)
            latlng = [float(i) for i in latlng]
            latlng_array.append(latlng)
            print(latlng_array)


    helpingfunction_fetchdata_unsimplified(latlng_array)
    return HttpResponse(template.render({},request))

def helpingfunction_fetchdata_unsimplified(latlng_array):
    global G
    #download street network
    #useful_tags = ox.settings.useful_tags_way + ['cycleway']
    #ox.config(use_cache=True, log_console=True, useful_tags_way=useful_tags)
    cf = '["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link|road|service|path|cycleway|footway|pedestrian"]'
    G = ox.graph_from_polygon(Polygon(latlng_array),custom_filter=cf,simplify=False)
    G_simplified = ox.simplify_graph(G, strict=True)
    ox.save_graph_geojson(G_simplified, filepath='static/geojson_files/streetnetwork_simplified')
    G = G_simplified


    #download buildings
    tags = {'building': True,
            'natural': True,
            'landuse': ['allotments', 'farmland', 'recreation_ground', 'village_green', 'forest', 'meadow', 'orchard',
                        'vineyard', 'basin', 'cemetry', 'brownfield', 'grass', 'greenfield', 'greenhouse_horticulture',
                        'landfill', 'plant_nursery', 'reservoir', 'salt_pond'],
            'leisure': ['garden', 'nature_reserve', 'park', 'pitch', 'playground', 'swimming_pool'],
            }
    buildings_gdf = ox.pois_from_polygon(Polygon(latlng_array),tags)
    buildings_gdf = buildings_gdf[['geometry','osmid','element_type']]
    buildings_gdf.to_file('static/geojson_files/buildings' + '.geojson', driver="GeoJSON", encoding="utf-8")

    #download other natural and manmade open spaces
   # tags = {'natural': True,
    #        'amenity': 'parking',
     #       'landuse' : [ 'allotments','farmland','recreation_ground','village_green','forest','meadow','orchard','vineyard','basin','cemetry','brownfield','grass','greenfield','greenhouse_horticulture','landfill','plant_nursery','reservoir','salt_pond'],
      #      'leisure' : ['garden','nature_reserve','park','pitch','playground','swimming_pool'],
       #     }
  #  openregions_gdf = ox.pois_from_polygon(Polygon(latlng_array), tags)
  #  openregions_gdf = openregions_gdf[['geometry', 'osmid', 'element_type']]
  #  openregions_gdf.to_file('static/geojson_files/openregions' + '.geojson', driver="GeoJSON", encoding="utf-8")

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


def requestFME(request):
    if request.is_ajax():
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
        Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
        Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
        Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
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
    Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
    Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
    Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
    
    base = open(Inputbasepath)
    sketch = open(Inputsketchpath)
    align = open(Inputaligndata)
    
    # returns JSON object as a dictionary
    data = json.load(align)
    amal_ids = []
    ng_ids = []
    c_ids =[]
    om_ids=[]
    s_amal_ids = []
    s_ng_ids = []
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
                    ng_id1 = val1['SketchAlign']['0']
                    s_ng_ids.append(ng_id1)

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
    align.close()

    data_ip = json.load(base)
    poly = []
    line = []
    point = []
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
                    else:
                        # Create a Polygon object
                        f_coor = geometry.Polygon(coor[0])
                        no_gen_p.append(f_coor)
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
    base.close()
    
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
    
    ng_res= ng_res_l + ng_res_p
    ng_res_f= [sublist for sublist in ng_res if sublist]
    
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
    for x, ids, sids in zip(ng_res_f, ng_ids, s_ng_ids):
        if len(x) == 0:  # Skip empty inputs
            continue
        if isinstance(x[0], shapely.geometry.linestring.LineString):
            line = shapely.geometry.LineString(x[0])
            wkt_string = line.wkt
            gen_type = "No generalization"
        elif isinstance(x[0], shapely.geometry.polygon.Polygon):
            polygon = shapely.geometry.Polygon(x[0])
            wkt_string = polygon.wkt
            gen_type = "No generalization"
        else:
            continue
        
        features.append(Feature(geometry=shapely.wkt.loads(wkt_string), properties={"genType": gen_type, "BaseAlign": ids[0], "SketchAlign": sids[0]}))
                        
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


    outputpath =  os.path.join(USER_PROJ_DIR,"generalizedoutputMap"+".json")
    if os.path.exists(outputpath):
        os.remove(outputpath)
    f = open(outputpath, "a+")
    f.write(json.dumps(combined_feature_collection,indent=4))
    f.close()
    
    return(json.dumps(combined_feature_collection,indent=4))



def omission_deadendstreets(request):
    template = loader.get_template('../templates/generalizingmaps.html')
    global G
    G2 = G.copy()

    culdesacs = [key for key, value in utils_graph.count_streets_per_node(G).items() if value == 1]
    G2.remove_nodes_from(culdesacs)
    ox.save_graph_geojson(G2, filepath='static/geojson_files/streetnetwork_simplified_deadend')
    return HttpResponse(template.render({}, request))



#@app.route("/mmReceiver", methods=["POST", "GET"])
def mmGeoJsonReceiver(request):
    template = loader.get_template('../templates/generalizingmaps.html')
    global SM_QCN_PATH
    global MM_QCN_PATH
    #global USER_PROJ_DIR
    fileName_full = str(request.POST.get('metricFileName'))
    MMGeoJsonData = request.POST.get('MMGeoJsonData')
    #print(type(MMGeoJsonData))
    MMGeoJsonData = json.loads(MMGeoJsonData)
    print("here is MMGeoJsonData:", MMGeoJsonData)
    # print("here svg file and content:",fileName_full, svgContent)
    fileName, extension = os.path.splitext(fileName_full)

    #smGeoJson = request.get_json()
    data_format = "geojson"
    map_type = "metric_map"

    MetricMap_QCNS = qualify_map.main_loader(fileName, MMGeoJsonData, data_format, map_type)
    print(MetricMap_QCNS)
    USER_PROJ_DIR = "QualitativeRelationsOutput"
    try:
        MM_QCN_PATH = os.path.join(USER_PROJ_DIR,fileName_full+".json")
        #filepath = './output/'+str("sketchMapID")+'.json'
        print("final file path. sm..",MM_QCN_PATH)

        if os.path.exists(MM_QCN_PATH):
            os.remove(MM_QCN_PATH)
        f = open(MM_QCN_PATH, "a+")
        f.write(json.dumps(MetricMap_QCNS,indent=4))
        f.close()
    except IOError:
        print("Metric map QCNs json path problem ")
    return HttpResponse(json.dumps(MetricMap_QCNS,indent=4))


"""
    - load sketch map geojson into qualifier 
"""


#@app.route("/smReceiver", methods=["POST", "GET"])
def smGeoJsonReceiver(request):
    template = loader.get_template('../templates/generalizingmaps.html')
    global SM_QCN_PATH
    global USER_PROJ_DIR

    fileName_full = str(request.POST.get('sketchFileName'))
    SMGeoJsonData = request.POST.get('SMGeoJsonData')
    SMGeoJsonData = json.loads(SMGeoJsonData)
    # print("here svg file and content:",fileName_full, svgContent)
    fileName, extension = os.path.splitext(fileName_full)
    #print("here is SMGeoJsonData:",SMGeoJsonData)
    #smGeoJson = request.get_json()
    data_format = "geojson"
    map_type = "sketch_map"

    sketchMap_QCNS = qualify_map.main_loader(fileName, SMGeoJsonData, data_format, map_type)
    USER_PROJ_DIR = "QualitativeRelationsOutput"
    try:
        SM_QCN_PATH = os.path.join(USER_PROJ_DIR,fileName_full+".json")
        #filepath = './output/'+str("sketchMapID")+'.json'
        print("final file path. sm..",SM_QCN_PATH)

        if os.path.exists(SM_QCN_PATH):
            os.remove(SM_QCN_PATH)
        f = open(SM_QCN_PATH, "a+")
        f.write(json.dumps(sketchMap_QCNS,indent=4))
        f.close()
    except IOError:
        print("Sketch map QCNs json path problem ")
    return HttpResponse(json.dumps(sketchMap_QCNS, indent=4))


def analyzeInputMap(request):
        sketchFileName = str(request.POST.get('sketchFileName'))
        metricFileName = str(request.POST.get('metricFileName'))
        print("name", sketchFileName, metricFileName)

        # session['sketchFileName'] = sketchFileName

        USER_PROJ_DIR = "QualitativeRelationsOutput"

        MM_QCN_PATH = os.path.join(USER_PROJ_DIR, metricFileName + ".json")
        SM_QCN_PATH = os.path.join(USER_PROJ_DIR, sketchFileName + ".json")

        print("MM_QCN_PATH", MM_QCN_PATH)
        print("SM_QCN_PATH", SM_QCN_PATH)
        with open(MM_QCN_PATH, 'r+') as mmjson:
            try:
                # print("reading path..",os.path.join(dir_qcns,'metric_map.json'))
                metricMapQCNs = json.load(mmjson)
            except IOError:
                print("metric_map.json is not loading ")

        with open(SM_QCN_PATH, 'r+') as smjson:
            try:
                sketchMapQCNs = json.load(smjson)
            except IOError:
                print("sketch_map.json is not loading ")

        total_mm_landmarks = completeness.get_landmarks_mm(metricMapQCNs)
        toal_mm_streets = completeness.get_streets_mm(metricMapQCNs)
        total_mm_cityblocks = completeness.get_cityblocks_mm(metricMapQCNs)


        totalSketchedLandmarks = completeness.get_landmarks_sm(sketchMapQCNs)
        totalSketchedStreets = completeness.get_streets_sm(sketchMapQCNs)
        totalSketchedCityblocks = completeness.get_cityblocks_sm(sketchMapQCNs)

        landmarkCompleteness = completeness.get_landmarkCompleteness(totalSketchedLandmarks, total_mm_landmarks)
        landmarkCompleteness = round(landmarkCompleteness, 2)
        # session['landmarkCompleteness'] = landmarkCompleteness

        streetCompleteness = completeness.get_streetCompleteness(totalSketchedStreets, toal_mm_streets)
        streetCompleteness = round(streetCompleteness, 2)
        # session['streetCompleteness'] = streetCompleteness

        cityblockCompleteness = completeness.get_cityblockCompleteness(totalSketchedCityblocks, total_mm_cityblocks)
        cityblockCompleteness = round(cityblockCompleteness, 2)
        # session['cityblockCompleteness'] = cityblockCompleteness
        overAllCompleteness = completeness.get_overall_completness(landmarkCompleteness, streetCompleteness,cityblockCompleteness)
        # session['overAllCompleteness'] = overAllCompleteness

        """
            Measure the correct relations using RCC11
        """
        totalRCC11Relations_mm = qualitativeAnalyser.getTotalRelations_rcc8_mm(metricMapQCNs)
        totalRCC11Relations = qualitativeAnalyser.getTotalRelations_rcc8_sm(sketchMapQCNs)
        correctRCC11Relations = qualitativeAnalyser.getCorrrctRelation_rcc8(sketchMapQCNs, metricMapQCNs)
        wrongMatchedRCC11rels = qualitativeAnalyser.getWrongRelations_rcc8(sketchMapQCNs, metricMapQCNs)
        missingRCC11rels = totalRCC11Relations_mm - (correctRCC11Relations + wrongMatchedRCC11rels)
        if correctRCC11Relations != 0 or totalRCC11Relations != 0:
            correctnessAccuracy_rcc11 = (correctRCC11Relations / totalRCC11Relations) * 100
        else:
            correctnessAccuracy_rcc11 = 0.00


        """
                Measure the correct relations using Linear Ordering 
                alogn the defined route 
            """
        total_lO_rels_mm = qualitativeAnalyser.getTotalLinearOrderingReltions_mm(metricMapQCNs)
        total_LO_rels_sm = qualitativeAnalyser.getTotalLinearOrderingReltions_sm(sketchMapQCNs)
        matched_LO_rels = qualitativeAnalyser.getCorrectRelation_linearOrdering(sketchMapQCNs, metricMapQCNs)
        wrong_matched_LO_rels = qualitativeAnalyser.getWrongRelations_linearOrdering(sketchMapQCNs, metricMapQCNs)
        missing_LO_rels = total_lO_rels_mm - (matched_LO_rels + wrong_matched_LO_rels)
        if matched_LO_rels != 0 or total_LO_rels_sm != 0:
            correctnessAccuracy_LO = (matched_LO_rels / total_LO_rels_sm) * 100
        else:
            correctnessAccuracy_LO = 0.00

        """
            Measure the correct relations using LeftRight
            alogn the defined route 
        """
        total_LR_rels_mm = qualitativeAnalyser.getTotalLeftRightRelations_mm(metricMapQCNs)
        total_LR_rels_sm = qualitativeAnalyser.getTotalLeftRightRelations_sm(sketchMapQCNs)
        matched_LR_rels = qualitativeAnalyser.getCorrectrelations_leftRight(sketchMapQCNs, metricMapQCNs)
        wrong_matched_LR_rels = qualitativeAnalyser.getWrongCorrectrelations_leftRight(sketchMapQCNs, metricMapQCNs)
        missing_LR_rels = total_LR_rels_mm - (matched_LR_rels + wrong_matched_LR_rels)
        if matched_LR_rels != 0 or total_LR_rels_sm != 0:
            correctnessAccuracy_LR = (matched_LR_rels / total_LR_rels_sm) * 100
        else:
            correctnessAccuracy_LR = 0.00

        """
            Measure the correct relations using Topologocal Relations between streets and regions 

        """
        total_DE9IM_rels_mm = qualitativeAnalyser.getTotalDE9IMRelations_mm(metricMapQCNs)
        total_DE9IM_rels_sm = qualitativeAnalyser.getTotalDE9IMRelations_sm(sketchMapQCNs)
        matched_DE9IM_rels = qualitativeAnalyser.getCorrectrelations_DE9IM(sketchMapQCNs, metricMapQCNs)
        wrong_matched_DE9IM_rels = qualitativeAnalyser.getWrongCorrectrelations_DE9IM(sketchMapQCNs, metricMapQCNs)
        missing_DE9IM_rels = total_DE9IM_rels_mm - (matched_DE9IM_rels + wrong_matched_DE9IM_rels)
        if matched_DE9IM_rels != 0 or total_DE9IM_rels_sm != 0:
            correctnessAccuracy_DE9IM = (matched_DE9IM_rels / total_DE9IM_rels_sm) * 100
        else:
            correctnessAccuracy_DE9IM = 0.00


        """
            Measure the correct relations using Topologocal Relations between streets  
        """
        total_streetTop_rels_mm = qualitativeAnalyser.getTotalStreetTopology_mm(metricMapQCNs)
        total_streetTop_rels_sm = qualitativeAnalyser.getTotalStreetTopology_sm(sketchMapQCNs)
        matched_streetTop_rels = qualitativeAnalyser.getCorrectrelations_streetTopology(sketchMapQCNs, metricMapQCNs)
        wrong_matched_streetTop_rels = qualitativeAnalyser.getWrongCorrectrelations_streetTopology(sketchMapQCNs,
                                                                                                   metricMapQCNs)
        missing_streetTop_rels = total_streetTop_rels_mm - (matched_streetTop_rels + wrong_matched_streetTop_rels)
        if matched_streetTop_rels != 0 or total_streetTop_rels_sm != 0:
            correctnessAccuracy_streetTop = (matched_streetTop_rels / total_streetTop_rels_sm) * 100
        else:
            correctnessAccuracy_streetTop = 0.00
        """
             Measure the correct relations using Orientation Relations between streets  
         """
        total_opra_rels_mm = qualitativeAnalyser.getTotalOPRA_mm(metricMapQCNs)
        total_opra_rels_sm = qualitativeAnalyser.getTotalOPRA_sm(sketchMapQCNs)
        matched_opra_rels = qualitativeAnalyser.getCorrectrelations_opra(sketchMapQCNs, metricMapQCNs)
        wrong_matched_opra_rels = qualitativeAnalyser.getWrongCorrectrelations_opra(sketchMapQCNs, metricMapQCNs)
        missing_opra_rels = total_opra_rels_mm - (matched_opra_rels + wrong_matched_opra_rels)
        if matched_opra_rels != 0 or total_opra_rels_sm != 0:
            correctnessAccuracy_opra = (matched_opra_rels / total_opra_rels_sm) * 100
        else:
            correctnessAccuracy_opra = 0.00

        """
               Calculate Recision and Recall 
         """
        total_no_correct_rels = correctRCC11Relations + matched_LO_rels + matched_LR_rels + matched_DE9IM_rels + matched_streetTop_rels + matched_opra_rels
        total_no_rels_sm = totalRCC11Relations + total_LO_rels_sm + total_LR_rels_sm + total_DE9IM_rels_sm + total_streetTop_rels_sm + total_opra_rels_sm
        total_on_rels_MM = totalRCC11Relations_mm + total_lO_rels_mm + total_LR_rels_mm + total_DE9IM_rels_mm + total_streetTop_rels_mm + total_opra_rels_mm
        precision = total_no_correct_rels / total_no_rels_sm
        recall = total_no_correct_rels / total_on_rels_MM

        #f_score = 2 * ((precision * recall) / (precision + recall))

        print("precision....:", precision)
        print("recall....:", recall)
        #print("F-value....:", f_score)
        # session.modified = True

        return HttpResponse(json.dumps({"sketchMapID": sketchFileName, "total_mm_landmarks": total_mm_landmarks,
                           "toal_mm_streets": toal_mm_streets, "total_mm_cityblocks": total_mm_cityblocks,
                           "totalSketchedLandmarks": totalSketchedLandmarks,
                           "totalSketchedStreets": totalSketchedStreets,
                           "totalSketchedCityblocks": totalSketchedCityblocks,
                           "landmarkCompleteness": landmarkCompleteness,
                           "streetCompleteness": streetCompleteness, "cityblockCompleteness": cityblockCompleteness,
                           "overAllCompleteness": round(overAllCompleteness, 2),
                           "totalRCC11Relations_mm": totalRCC11Relations_mm, "totalRCC11Relations": totalRCC11Relations,
                           "correctRCC11Relations": correctRCC11Relations,
                           "wrongMatchedRCC11rels": wrongMatchedRCC11rels,
                           "missingRCC11rels": missingRCC11rels,
                           "correctnessAccuracy_rcc11": round(correctnessAccuracy_rcc11, 2),
                           "total_lO_rels_mm": total_lO_rels_mm, "total_LO_rels_sm": total_LO_rels_sm,
                           "matched_LO_rels": matched_LO_rels, "wrong_matched_LO_rels": wrong_matched_LO_rels,
                           "missing_LO_rels": missing_LO_rels,
                           "correctnessAccuracy_LO": round(correctnessAccuracy_LO, 2),
                           "total_LR_rels_mm": total_LR_rels_mm,
                           "total_LR_rels_sm": total_LR_rels_sm, "matched_LR_rels": matched_LR_rels,
                           "wrong_matched_LR_rels": wrong_matched_LR_rels, "missing_LR_rels": missing_LR_rels,
                           "correctnessAccuracy_LR": round(correctnessAccuracy_LR, 2),
                           "total_DE9IM_rels_mm": total_DE9IM_rels_mm, "total_DE9IM_rels_sm": total_DE9IM_rels_sm,
                           "matched_DE9IM_rels": matched_DE9IM_rels,
                           "wrong_matched_DE9IM_rels": wrong_matched_DE9IM_rels,
                           "missing_DE9IM_rels": missing_DE9IM_rels,
                           "correctnessAccuracy_DE9IM": round(correctnessAccuracy_DE9IM, 2),
                           "total_streetTop_rels_mm": total_streetTop_rels_mm,
                           "total_streetTop_rels_sm": total_streetTop_rels_sm,
                           "matched_streetTop_rels": matched_streetTop_rels,
                           "wrong_matched_streetTop_rels": wrong_matched_streetTop_rels,
                           "missing_streetTop_rels": missing_streetTop_rels,
                           "correctnessAccuracy_streetTop": round(correctnessAccuracy_streetTop, 2),
                           "total_opra_rels_mm": total_opra_rels_mm, "total_opra_rels_sm": total_opra_rels_sm,
                           "matched_opra_rels": matched_opra_rels, "wrong_matched_opra_rels": wrong_matched_opra_rels,
                           "missing_opra_rels": missing_opra_rels,
                           "correctnessAccuracy_opra": round(correctnessAccuracy_opra, 2),
                           "precision": round(precision, 2),
                           "recall": round(recall, 2),
                           "f_score": "nil"}), content_type="application/json")