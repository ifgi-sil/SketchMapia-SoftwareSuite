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
import math
import bcrypt
from shapely import geometry, ops
from shapely.geometry import Point, Polygon, shape
from shapely import LineString, MultiPoint, Polygon
from matplotlib import pyplot as plt
import shapely.wkt
from math import sqrt
import geojson
from geojson import Feature, Point, FeatureCollection, Polygon, dump
from django.http import JsonResponse
from collections import defaultdict


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
    Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
    Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
    Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
    
    base = open(Inputbasepath)
    sketch = open(Inputsketchpath)
    align = open(Inputaligndata)
    # breakpoint()
    # returns JSON object as a dictionary
    data_ip = json.load(base)
    data = json.load(align)
    amal_ids = []
    ng_id_1 = []
    c_ids =[]
    om_ids=[]
    a2e_ids =[]
    s_amal_ids =[]
    # s_ng_ids = []
    s_c_ids =[]
    s_om_ids=[]
    s_a2e_ids =[]
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
                    ng_id_1.append(ng_id)
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
                    
                if val1[key]== "Abstraction to show existence":
                    a2e_id = val1['BaseAlign']['0']
                    a2e_ids.append(a2e_id)
                    a2e_id1 = val1['SketchAlign']['0']
                    s_a2e_ids.append(a2e_id1)

            except (KeyError,TypeError) as error:
                continue
            
    m_ids =[]
    m_coor= []
    for i in data_ip['features']:
        geo = i['geometry']
        properties = i['properties']
        id = properties['id']
        
        if i['properties'].get('missing'):
            m_ids.append(i['properties']['id'])
            m_coor.append(i['geometry']['coordinates'])
            
    def calculate_angle(p1, p2, p3):
        """
        Calculate the angle between three points.
        """
        def vector(a, b):
            return [b[0] - a[0], b[1] - a[1]]

        v1 = vector(p1, p2)
        v2 = vector(p2, p3)

        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        magnitude1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        magnitude2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if magnitude1 * magnitude2 == 0:
            return 0

        cos_angle = dot_product / (magnitude1 * magnitude2)
        angle = math.acos(min(1, max(cos_angle, -1)))  # Ensure value is within [-1, 1] for acos

        return math.degrees(angle)

    def is_curved(coordinates, curvature_threshold=30):
        """
        Check if a sequence of coordinates represents a curved path.
        """
        for j in range(1, len(coordinates) - 1):
            angle = calculate_angle(coordinates[j-1], coordinates[j], coordinates[j+1])
            if angle < 180 - curvature_threshold:
                return True
        return False

    def check_closed_loop(coordinates):
        """
        Check if a sequence of coordinates forms a closed loop.
        """
        return coordinates[0] == coordinates[-1]

    
    def is_connected(coord1, coord2):
        """
        Check if the end of coord1 is the start of coord2.
        """
        return coord1[-1] == coord2[0]
    
    
    # def combine_segments(m_ids, m_coor):
    #     """
    #     Combine segments that are connected and track their IDs.
    #     """
    #     combined_segments = []
    #     visited = set()

    #     for i, (segment, segment_id) in enumerate(zip(m_coor, m_ids)):
    #         if i in visited:
    #             continue

    #         current_path = segment[:]
    #         segment_ids = [segment_id]

    #         for j in range(i + 1, len(m_coor)):
    #             if j in visited:
    #                 continue

    #             if is_connected(current_path, m_coor[j]):
    #                 current_path.extend(m_coor[j][1:])
    #                 segment_ids.append(m_ids[j])
    #                 visited.add(j)

    #         combined_segments.append((segment_ids, current_path))
    #         visited.add(i)

    #     return combined_segments

    def combine_segments(m_ids, m_coor):
        """
        Combine segments that are connected and track their IDs.
        """
        def find_connected_segments(start_coord, segments, segment_ids, visited):
            path = []
            path_ids = []
            for i, (segment, segment_id) in enumerate(zip(segments, segment_ids)):
                if i not in visited:
                    if segment[0] == start_coord:
                        visited.add(i)
                        path.extend(segment[1:])
                        path_ids.append(segment_id)
                        p, p_ids = find_connected_segments(segment[-1], segments, segment_ids, visited)
                        path.extend(p)
                        path_ids.extend(p_ids)
                    elif segment[-1] == start_coord:
                        visited.add(i)
                        path.extend(segment[:-1][::-1])
                        path_ids.append(segment_id)
                        p, p_ids = find_connected_segments(segment[0], segments, segment_ids, visited)
                        path.extend(p)
                        path_ids.extend(p_ids)
            return path, path_ids
        
        combined_segments = []
        visited = set()
        for i, (segment, segment_id) in enumerate(zip(m_coor, m_ids)):
            if i not in visited:
                visited.add(i)
                combined_path = segment[:]
                combined_ids = [segment_id]
                p, p_ids = find_connected_segments(segment[-1], m_coor, m_ids, visited)
                combined_path.extend(p)
                combined_ids.extend(p_ids)
                combined_segments.append((combined_ids, combined_path))
        
        return combined_segments

    def check_curvature_and_loop(m_ids, m_coor, curvature_threshold=30):
        """
        Check which streets are curved and if they form closed loops.
        """
        curved_ids = []
        loop_ids = []
        straight_ids = []
        # breakpoint()
        
        # combined_segments = combine_segments(m_coor)

        # for segment_ids, coordinates in combined_segments:
        #     if is_curved(coordinates, curvature_threshold):
        #         curved_ids.extend([m_ids[i] for i in segment_ids])

        #     if check_closed_loop(coordinates):
        #         loop_ids.extend([m_ids[i] for i in segment_ids])
        #     else:
        #         straight_ids.extend([m_ids[i] for i in segment_ids])
        combined_segments = combine_segments(m_ids, m_coor)

        for segment_ids, coordinates in combined_segments:
            if is_curved(coordinates, curvature_threshold):
                curved_ids.extend(segment_ids)

            if check_closed_loop(coordinates):
                loop_ids.append(segment_ids)
            else:
                straight_ids.append(segment_ids)
        
        curved_ids = list(set(curved_ids))
        # loop_ids = list(set(loop_ids))
        # straight_ids = list(set(straight_ids))
        
        return {
            "curved_ids": curved_ids,
            "loop_ids": loop_ids,
            "straight_ids": straight_ids
        }
        
    result = check_curvature_and_loop(m_ids, m_coor)
    
    loop_ids = result["loop_ids"]
    st_ids = result["straight_ids"]
    print("Curved IDs:", result["curved_ids"])
    print("Loop IDs:", result["loop_ids"])
    print("Straight IDs:", result["straight_ids"])
    
    # breakpoint()
    
    def extract_endpoints(coordinates):
        """
        Extract the endpoints from a set of coordinates.
        """
        start = coordinates[0]
        end = coordinates[-1]
        return start, end

    # Function to find connected streets and their coordinates
    def find_connected_streets(loop_ids, all_segments):
        """
        Find streets that are connected to the streets forming a closed loop.
        """
        connected_streets = []
        connected_street_points = []

        if isinstance(loop_ids[0], int):
            loop_ids = [loop_ids]

        # Step 1: Process each loop group separately
        for loop_group in loop_ids:
            loop_endpoints = []
            loop_segments = []
        
            # Identify endpoints of segments in loop_ids and store them in loop_endpoints
            for segment in all_segments['features']:
                properties = segment['properties']
                segment_id = properties['id']
                if segment_id in loop_group:
                    geometry = segment['geometry']
                    segment_coor = geometry['coordinates']
                    start, end = extract_endpoints(segment_coor)
                    
                    loop_endpoints.append(start)
                    loop_endpoints.append(end)
                    loop_segments.append((segment_id, start, end))
        
            connected_streets_ids = []
            connected_street_coords = []
            
            # Find segments connected to loop segments
            for loop_endpoint in loop_endpoints:
                for segment in all_segments['features']:
                    properties = segment['properties']
                    segment_id = properties['id']
                    if segment_id in loop_group:
                        continue  # Skip segments that are already part of the loop
                    geometry = segment['geometry']
                    segment_coor = geometry['coordinates']
                    start, end = extract_endpoints(segment_coor)
                    
                    # Check if the start or end point of the segment matches any loop endpoint
                    if start == loop_endpoint or end == loop_endpoint:
                        if segment_id not in connected_streets_ids:
                            connected_streets_ids.append(segment_id)
                        if start == loop_endpoint:
                            connected_street_coords.append(start)
                        elif end == loop_endpoint:
                            connected_street_coords.append(end)

            unique_coords = list(set(tuple(coord) for coord in connected_street_coords))
            unique_coords = [list(coord) for coord in unique_coords]
            # breakpoint()
            connected_streets.append(connected_streets_ids)
            connected_street_points.append(unique_coords)
            
        return connected_streets, connected_street_points


    # Call the function and get the results
    connected_streets, connected_street_points = find_connected_streets(loop_ids, data_ip)
    
    connected_streets_st, st_points = find_connected_streets(st_ids, data_ip)

    # Print the results
    print("Connected Streets IDs:", connected_streets)
    print("Connected Streets points:", connected_street_points)
    print("Connected Streets straight IDs:", connected_streets_st)
    print("Connected Streets straight points:", st_points)
    
    # Flatten list2 for easier comparison with list1
    # flattened_list2 = [item[0] for item in ng_id_1]

    # Create the final list by excluding elements in list1
    # ng_ids = [[item] for item in flattened_list2 if item not in connected_streets and item not in connected_streets_st]
    
        # Flatten connected_streets and connected_streets_st for easier comparison
    flattened_connected_streets = [item for sublist in connected_streets for item in sublist]
    flattened_connected_streets_st = [item for sublist in connected_streets_st for item in sublist]

    # Create the final list by excluding elements in connected_streets and connected_streets_st
    ng_ids = [
        [item for item in sublist if item not in flattened_connected_streets and item not in flattened_connected_streets_st]
        for sublist in ng_id_1
    ]

    # Remove empty sublists
    ng_ids = [sublist for sublist in ng_ids if sublist]
    
    print(ng_ids)
    
    # breakpoint()

    poly = []
    line = []
    point = []
    a2e_l = []
    a2e_p= []
    a2e_ids_l=[]
    a2e_ids_p=[]
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
                
        for x in a2e_ids:
            for y in x:
                if y == id :
                    type = geo['type']
                    coor = geo['coordinates']
                    if len(coor) > 1:
                        # Create a LineString object
                        f_coor = geometry.LineString(coor)
                        a2e_l.append(f_coor)
                        a2e_ids_l.append(id)
                    else:
                        # Create a Polygon object
                        f_coor = geometry.Polygon(coor[0])
                        a2e_p.append(f_coor)
                        a2e_ids_p.append(id)
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
        
    a2e_l_res = []
    for sublist in a2e_ids:
        start = sum([len(sub) for sub in a2e_l_res])
        end = start + len(sublist)
        a2e_l_res.append(a2e_l[start:end])
        
    a2e_p_res=[]   
    for sublist in a2e_ids:
        start = sum([len(sub) for sub in a2e_p_res])
        end = start + len(sublist)
        a2e_p_res.append(a2e_p[start:end])
        
    s_ng_ids_l = []
    s_ng_ids_p = []
    s_a2e_ids_l = []
    s_a2e_ids_p = []
    s_rac_ids =[]
    s_jm_ids = []
    
    def is_in_nested_list(nested_list, value):
        return any(value in sublist for sublist in nested_list)
    
    # Iterate through the data and update SketchAlign
    for key, value in data.items():
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, dict) and "BaseAlign" in sub_value:
                base_align_value = sub_value["BaseAlign"]["0"][0]
                sketch_align_value = sub_value["SketchAlign"]["0"]
                
                if base_align_value in ng_ids_p:
                    s_ng_ids_p.append(sketch_align_value)
                elif base_align_value in ng_ids_l:
                    s_ng_ids_l.append(sketch_align_value)
                if base_align_value in a2e_ids_p:
                    s_a2e_ids_p.append(sketch_align_value)
                elif base_align_value in a2e_ids_l:
                    s_a2e_ids_l.append(sketch_align_value)
                if is_in_nested_list(connected_streets, base_align_value):
                    s_rac_ids.append(sketch_align_value)
                if is_in_nested_list(connected_streets_st, base_align_value):
                    s_jm_ids.append(sketch_align_value)
    # breakpoint()
    # Iterate through the data and update SketchAlign
    # for key, value in data.items():
    #     for sub_key, sub_value in value.items():
    #         if isinstance(sub_value, dict) and "BaseAlign" in sub_value and "SketchAlign" in sub_value:
    #             base_align_list = sub_value["BaseAlign"]["0"]
    #             sketch_align_list = sub_value["SketchAlign"]["0"]
                
    #             # Ensure both lists have the same length
    #             if len(base_align_list) != len(sketch_align_list):
    #                 print(f"Warning: Mismatched lengths for BaseAlign and SketchAlign in {key} -> {sub_key}")
    #                 continue
                
    #             # Pair elements and append to the appropriate lists
    #             for base_align_value, sketch_align_value in zip(base_align_list, sketch_align_list):
    #                 if base_align_value in ng_ids_p:
    #                     s_ng_ids_p.append(sketch_align_value)
    #                 elif base_align_value in ng_ids_l:
    #                     s_ng_ids_l.append(sketch_align_value)
    #                 if base_align_value in a2e_ids_p:
    #                     s_a2e_ids_p.append(sketch_align_value)
    #                 elif base_align_value in a2e_ids_l:
    #                     s_a2e_ids_l.append(sketch_align_value)

    # align.close()
    # base.close()
    features = []
    
    # breakpoint()
    # amalgamation .................................................................
    for x, ids, sids in zip(poly_res, amal_ids, s_amal_ids):
        mpt = geometry.MultiPolygon(x)
        res = mpt.convex_hull.wkt
        g1_a = shapely.wkt.loads(res)
        features.append(Feature(geometry=g1_a, properties={"genType": "Amalgamation", "BaseAlign": ids, "SketchAlign":sids[0]}))

    # omission_merge................................................................
    for x, ids, sids in zip(line_res, om_ids, s_om_ids):
        multi_line = geometry.MultiLineString(x)
        merged_line = ops.linemerge(multi_line)
        g1_o = shapely.wkt.loads(str(merged_line))
        features.append(Feature(geometry=g1_o, properties={"genType": "OmissionMerge", "BaseAlign": ids[0],"SketchAlign":sids[0]}))
   
    # collapse......................................................................
    for x, ids, sids in zip(point_res, c_ids, s_c_ids):
        collapse = x[0].centroid
        g1_c = shapely.wkt.loads(str(collapse))
        features.append(Feature(geometry=g1_c, properties={"genType": "Collapse", "BaseAlign": ids[0],"SketchAlign":sids[0]}))
        
    def is_connected(multi_line):
        merged = ops.linemerge(multi_line)
        if isinstance(merged, geometry.LineString):
            return True
        elif isinstance(merged, geometry.MultiLineString) and len(merged.geoms) == 1:
            return True
        return False
    
    # Abstraction to show existence Streets and buildings ..........................
    for x, ids, sids in zip(a2e_l_res, a2e_ids, s_a2e_ids_l):
        # breakpoint()
        if len(x) == 0: # Skip empty inputs
            continue
        multi_line = geometry.MultiLineString(x)
        if is_connected(multi_line):
            merged_line = ops.linemerge(multi_line)
            g1_a2e = geometry.shape(merged_line)
            gen_type = "Multi-MultiOmissionMerge"
            features.append(Feature(geometry=g1_a2e, properties={"genType3": gen_type, "BaseAlign": ids, "SketchAlign":sids}))
        else:
            g1_a2e = multi_line
            gen_type = "Abstraction to show existence"
            features.append(Feature(geometry=g1_a2e, properties={"genType": gen_type, "BaseAlign": ids, "SketchAlign":sids}))
    
    for x, ids, sids in zip(a2e_p_res, a2e_ids_p, s_a2e_ids_p):
        if len(x) == 0: # Skip empty inputs
            continue
        # breakpoint()
        mpt = geometry.MultiPolygon(x)
        res = mpt.convex_hull.wkt
        g1_a2e = shapely.wkt.loads(res)
        features.append(Feature(geometry=g1_a2e, properties={"genType": "Abstraction to show existence", "BaseAlign": ids, "SketchAlign":sids}))

    # No Generalization .............................................................
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
    
    # Roundabout Collapse ...........................................................
    sketch = open(Inputsketchpath)
    sketchdata= json.load(sketch)
    s_rac_l = []
    # print(s_rac_ids)
    # breakpoint()
    for sublist in s_rac_ids:
        for sid in sublist:
            for feature in sketchdata['features']:
                if feature['properties']['sid'] == sid:
                    s_rac_l.append(geometry.LineString(feature['geometry']['coordinates']))
                    
    s_rac_l_res = []
    for sublist in s_rac_ids:
        start = sum([len(sub) for sub in s_rac_l_res])
        end = start + len(sublist)
        s_rac_l_res.append(s_rac_l[start:end])
        
    def connection_check (s_rac_l_res, connected_streets, s_rac_ids):
        for x, ids, sids in zip(s_rac_l_res, connected_streets, s_rac_ids):
            multi_line = geometry.MultiLineString(x)
            # breakpoint()
            if is_connected(multi_line):
                return 'connected'
            else:
                return 'not connected'

    def find_features(data_ip, loop_ids):
        rac_l_res = []
        if isinstance(loop_ids[0], int):
            loop_ids = [loop_ids]
            
        for loop_group in loop_ids:
            rac_l =[]
            for feature in data_ip['features']:
                geo = feature['geometry']
                properties = feature['properties']
                id = properties['id']
                
                if id in loop_group:
                    type = geo['type']
                    coor = geo['coordinates']
                    if type == 'LineString':
                        f_coor = geometry.LineString(coor)
                        rac_l.append(f_coor)
            rac_l_res.append(rac_l)
        return rac_l_res
    
    connection_status = connection_check(s_rac_l_res, connected_streets, s_rac_ids)

    # Only proceed if connected
    if connection_status == 'connected':
        rac_l_res = find_features(data_ip, loop_ids)
        # print(rac_l_res)
        # breakpoint()    
        # multi_line = geometry.MultiLineString(rac_l_res)
        centroids = []
        
        for group in rac_l_res:
            # Create a MultiLineString from the current group
            multi_line = geometry.MultiLineString(group)
            
            # Calculate the centroid of the MultiLineString
            centroid1 = multi_line.centroid
            centroids.append(centroid1)
    
        print(centroids) 

      
  
    # g_rac_line =[]
    # for group_index, street_group in enumerate(connected_streets):
    #     g_rac_lines =[]
    #     for feature in data_ip['features']:
    #             geo = feature['geometry']
    #             properties = feature['properties']
    #             id = properties['id']

    #             if id in street_group:
    #                 type = geo['type']
    #                 coor = geo['coordinates']
    #                 if type == 'LineString':
    #                     f_coor = geometry.LineString(coor)
    #                     g_rac_lines.append(f_coor)
    #     g_rac_line.append(g_rac_lines)

    # def extract_endpoint(line):
    #     return [line.coords[0], line.coords[-1]]
    
    # # Create new line segments that connect each endpoint to the centroid
    # new_segments = []
    # for line in g_rac_line:
    #     endpoints = extract_endpoint(line)
    #     # breakpoint()
    #     for endpoint in endpoints:
    #         new_segment = LineString([endpoint, (centroid.x, centroid.y)])
    #         new_segments.append(new_segment)

    # # Combine original line segments with new segments
    # all_segments = g_rac_line + new_segments

    # # Printing the results
    # for segment in all_segments:
    #     print(segment)
    
    # Iterate through connected streets and centroids to create new line segments
    # all_segments = []

    # for group_index, street_group in enumerate(connected_streets):
    #     centroid = centroids[group_index]
    #     g_rac_line = []
        
    #     for feature in data_ip['features']:
    #         geo = feature['geometry']
    #         properties = feature['properties']
    #         segment_id = properties['id']
            
    #         if segment_id in street_group:
    #             coor = geo['coordinates']
    #             if geo['type'] == 'LineString':
    #                 f_coor = LineString(coor)
    #                 g_rac_line.append(f_coor)
        
    #     new_segments = []
    #     for line in g_rac_line:
    #         endpoints = extract_endpoint(line)
    #         # for endpoint in endpoints:
    #         # print (line, endpoints)
    #         # breakpoint()
    #         new_segment = LineString([endpoints[0], (centroid.x, centroid.y)])
    #         new_segments.append(new_segment)

    #     all_segments.append(new_segments)

   # Iterate over the line segments
    # for i, line_segments in enumerate(g_rac_line):
    #     centroid = centroids[i]  # Select the corresponding centroid
        
    #     for line_segment in line_segments:
    #         line_coords = list(line_segment.coords)
    #         new_line_coords = [line_coords[0], line_coords[-1], centroid.coords[0]]
    #         new_line_segment = LineString(new_line_coords)
    #         print(new_line_segment)

                # new_segments.append(new_line_segment)
            
    # Printing the results
    # for segment in all_segments:
    #     print(segment)
    
    new_line = []
    
    for group_index, point_group in enumerate(connected_street_points):
        centroid = centroids[group_index]
        
        unique_points = set(tuple(point) for point in point_group)
    
        # Create new line segments joining each point to the centroid
        for point in unique_points:
            new_segment = LineString([point, (centroid.x, centroid.y)])
            new_line.append(new_segment)
            
    # breakpoint()      
    # for group_index, street_group in enumerate(connected_streets):
    #     centroid = centroids[group_index]
    #     # street_group = connected_streets[group_index]
        
    #     for segment_id in street_group:
    #         for feature in data_ip['features']:
    #             properties = feature['properties']
    #             geo = feature['geometry']
    #             if properties['id'] == segment_id:
    #                 coor = geo['coordinates']
    #                 if geo['type'] == 'LineString':
    #                     line = LineString(coor)
    #                     # endpoints = extract_endpoint(line)
    #                     # breakpoint()
    #                     # unique_points = set(tuple(point) for point in point_group)
    #                     # for point in unique_points:
    #                     #     new_segment = LineString([point, (centroid.x, centroid.y)])
                            
    #                         if line.coords[-1] == new_segment.coords[0]:
    #                             combined_segment = LineString(list(line.coords) + list(new_segment.coords[1:]))
    #                             print(combined_segment)
                            
    #                             # Create new feature for the extended line segment
    #                             new_feature = Feature(
    #                                 geometry=combined_segment,
    #                                 properties={
    #                                     "genType": "Roundaboutcollapse",
    #                                     "BaseAlign": segment_id,
    #                                     "SketchAlign": group_index  # Assuming SketchAlign should be group_index
    #                                 }
    #                             )
                        
    #                             # Add the new feature to the features list
    #                             features.append(new_feature)


    
            
    for group_index, street_group in enumerate(connected_streets):
        for segment_id in street_group:
            for feature in data_ip['features']:
                properties = feature['properties']
                geo = feature['geometry']
                if properties['id'] == segment_id and geo['type'] == 'LineString':
                    original_line = LineString(geo['coordinates'])
                    combined_segment = None  # Initialize combined_segment as None
                    
                    # Find the corresponding new line segment
                    for new_segment in new_line:
                        if original_line.coords[-1] == new_segment.coords[0]:
                            combined_segment = LineString(list(original_line.coords) + list(new_segment.coords[1:]))
                            break  # Exit the loop once combined_segment is found
                        elif original_line.coords[0] == new_segment.coords[0]:
                            combined_segment = LineString(list(new_segment.coords[1:]) + list(original_line.coords))
                            break  # Exit the loop once combined_segment is found
                    
                    # Ensure combined_segment is assigned
                    if combined_segment:
                        # print(combined_segment)
                        sketch_align_value = None
                        for key, value in data.items():
                            for val,val1 in v.items():
                                base_align_list = val1['BaseAlign']['0']
                                if segment_id in base_align_list:
                                    sketch_align_value = val1['SketchAlign']['0'][0]
                                    break 
                        # print(segment_id, sketch_align_value)
                        # breakpoint()
                        # Create new feature for the extended line segment
                        new_feature = Feature(
                            geometry=combined_segment,
                            properties={
                                "genType": "No generalization",
                                "genType1": "Roundaboutcollapse",
                                "BaseAlign": segment_id,
                                "SketchAlign": sketch_align_value,
                                "RoundAboutCount": len(connected_streets)
                            }
                        )

                        # Add the new feature to the features list
                        features.append(new_feature)

    # breakpoint() 

    # print(features)

    import matplotlib.pyplot as plt

    # fig, ax = plt.subplots()
    # for segment in new_segment:
    #     x, y = segment.xy
    #     ax.plot(x, y)
    # ax.plot(centroid.x, centroid.y, 'ro')  # plot centroid
    # plt.show()
    
    # breakpoint()
    
    # Junction merge.................................................................
    s_jm_l = []
    for sublist in s_jm_ids:
        for sid in sublist:
            for feature in sketchdata['features']:
                if feature['properties']['sid'] == sid:
                    s_jm_l.append(geometry.LineString(feature['geometry']['coordinates']))
                    
    s_jm_l_res = []
    for sublist in s_jm_ids:
        start = sum([len(sub) for sub in s_jm_l_res])
        end = start + len(sublist)
        s_jm_l_res.append(s_jm_l[start:end])
    
    connection_status = connection_check(s_jm_l_res, connected_streets_st, s_jm_ids)
    # breakpoint()
    def find_center_point_of_segment(line_segments):
        """
        Find the center points of all line segments.
        :param line_segments: A list of Shapely LineString objects representing the line segments.
        :return: A list of Shapely Point objects representing the center points of the line segments.
        """
        center_points = []
        for line_segment in line_segments:
            for line in line_segment:
                if isinstance(line, LineString):
                    coords = list(line.coords)
                    if len(coords) != 2:
                        raise ValueError("Each line segment must have exactly two endpoints.")
                    midpoint_x = (coords[0][0] + coords[1][0]) / 2
                    midpoint_y = (coords[0][1] + coords[1][1]) / 2
                    center_point = geometry.Point(midpoint_x, midpoint_y)
                    center_points.append(center_point)
                
        return center_points

    g_jm_line =[]
    for feature in data_ip['features']:
            geo = feature['geometry']
            properties = feature['properties']
            id = properties['id']

            for i in connected_streets_st:
                if id in i:
                    type = geo['type']
                    coor = geo['coordinates']
                    if type == 'LineString':
                        f_coor = geometry.LineString(coor)
                        g_jm_line.append((id,f_coor))

    print(g_jm_line)
    
    def extract_relevant_point(line, st_points):
        coords = list(line.coords)
        
        def point_in_st_points(point):
            """ Check if a given point is in st_points. """
            for group in st_points:
                for st_point in group:
                    if tuple(st_point) == point:
                        return True
            return False

        # Check if the line is curved (more than two points)
        if len(coords) > 2:
            # Check if the start or end of the line is in st_points
            if point_in_st_points(coords[0]):
                return coords[1:]  # Take the point next to the start point
            elif point_in_st_points(coords[-1]):
                return coords[:-1]  # Take the point before the end point
            else:
                # If neither start nor end is in st_points, return the second-to-last point
                return None

        else:
            # For straight lines, return the endpoint that is in st_points
            if point_in_st_points(coords[0]):
                return coords[-1]
            elif point_in_st_points(coords[-1]):
                return coords[0]
            else:
            #     # If neither endpoint is in st_points, return the first coordinate by default
                return None

    
    # def find_center_points_of_segments(line_segments):
    #     """
    #     Find center points for each group of 4 line segments.
    #     :param line_segments: A list of Shapely LineString objects.
    #     :return: A list of Shapely Point objects representing the center points.
    #     """
    #     center_points = []
    #     num_segments = len(line_segments)
        
    #     for i in range(0, num_segments, 4):
    #         segment_group = line_segments[i:i+4]
            
    #         if len(segment_group) < 4:
    #             print(f"Warning: Last group has less than 4 segments. Skipping group: {segment_group}")
    #             continue
            
    #         center_point = find_center_point_of_segment(segment_group[0])
    #         center_points.append(center_point)
        
    #     return center_points

    def create_junction_segments(line_segments, center_point, st_points):
        """
        Create junction segments by extending each line segment to the center point.
        :param line_segments: A list of Shapely LineString objects representing the line segments.
        :param center_point: A Shapely Point object representing the center point.
        :return: A list of new Shapely LineString objects.
        """
        new_segments = []
        for segment_id, line in line_segments:
            # endpoints = extract_relevant_point(line,st_points)
            # breakpoint()
            # print(line)
            # print(endpoints)
            relevant_point = extract_relevant_point(line, st_points)
            # print(relevant_point)
            if relevant_point is not None:
                if relevant_point == list(line.coords[1:]):
                # relevant_point is the result of coords[1:], so append center_point
                    new_segment = LineString([(center_point.x, center_point.y)] + list(relevant_point))
                elif relevant_point == list(line.coords[:-1]):
                    # relevant_point is the result of coords[:-1], so prepend center_point
                    new_segment = LineString(list(relevant_point) + [(center_point.x, center_point.y)])
                else:
                    # This handles cases where relevant_point is a single coordinate or an unexpected format
                    new_segment = LineString([relevant_point, (center_point.x, center_point.y)])
                
                # new_segments.append(new_segment)
                new_segments.append((segment_id, new_segment))
        
        return new_segments

    def process_line_segments(g_jm_line, center_points):
        """
        Process line segments by splitting into groups of 4, finding center points, and creating junction segments.
        :param jm_l_res: A list of Shapely LineString objects representing the line segments.
        :return: A list of new Shapely LineString objects representing the junctions.
        """
        new_segments = []
    
        # Split jm_l_line into groups of 4 and create junction segments
        num_segments = len(g_jm_line)
        num_center_points = len(center_points)
        
        if num_center_points * 4 != num_segments:
            print(f"Warning: Number of center points ({num_center_points}) and line segments ({num_segments}) do not align perfectly in 4:1 ratio. Skipping processing.")
            return new_segments

        for i in range(0, num_segments, 4):
            segment_group = g_jm_line[i:i+4]
            
            if len(segment_group) < 4:
                print(f"Warning: Last group has less than 4 segments. Skipping group: {segment_group}")
                continue
        
            # Create junction segments for the group
            center_point = center_points[i // 4]
            junction_segments = create_junction_segments(segment_group, center_point, st_points)
            # print(junction_segments)
            # breakpoint()
            # Add the new junction segments to the list
            new_segments.extend(junction_segments)
        print(new_segments)
        
        return new_segments

    # # Example usage:
    # if connection_status == 'connected':
    #     jm_l_res = find_features(data_ip, st_ids)
    #     breakpoint()
    # Process the line segments to create junctions
    # new_segments = process_line_segments(g_jm_line)
    
  
    
    # Combine original line segments with new segments
    # all_segments = g_jm_line + new_segments

    # Printing the results
    # for segment in all_segments:
    #     print(segment)
    

    # def plot_segments_and_centers(line_segments, center_points, all_segments):
    #     """
    #     Plot line segments and center points using Matplotlib.
    #     :param line_segments: A list of Shapely LineString objects.
    #     :param center_points: A list of Shapely Point objects.
    #     :param new_segments: A list of new Shapely LineString objects representing the junctions.
    #     """
    #     fig, ax = plt.subplots()
        
    #     # Plot original line segments
    #     for line in line_segments:
    #         x, y = line.xy
    #         ax.plot(x, y, color='blue', linestyle='dashed')
        
    #     # Plot center points
    #     for point in center_points:
    #         ax.plot(point.x, point.y, 'ro')  # 'ro' means red color, circle marker
        
    #     # Plot new junction segments
    #     for segment in all_segments:
    #         x, y = segment.xy
    #         ax.plot(x, y, color='green')
        
    #     plt.xlabel('X Coordinate')
    #     plt.ylabel('Y Coordinate')
    #     plt.title('Line Segments, Center Points, and Junctions')
    #     plt.grid(True)
    #     plt.show()
        
    # breakpoint() 
    # Only proceed if connected
    if connection_status == 'connected':
        jm_l_res = find_features(data_ip, st_ids)
        print(jm_l_res)
        
        # Assuming jm_l_res contains Shapely LineString objects
        center_points = find_center_point_of_segment(jm_l_res)
        
        print(center_points)
        # for points in center_points:
        #     print(points)
        # breakpoint()  
        # Process the line segments to create junctions
        new_segments = process_line_segments(g_jm_line, center_points)
        
        for segment_id, new_segment in new_segments:
            sketch_align_value = None
            for key, value in data.items():
                for val,val1 in v.items():
                    base_align_list = val1['BaseAlign']['0']
                    if segment_id in base_align_list:
                        sketch_align_value = val1['SketchAlign']['0'][0]
                        break 
                
            # print(segment_id, sketch_align_value)
            # breakpoint()
            new_feature = Feature(
                geometry=new_segment,
                properties={
                    "genType": "No generalization",
                    "genType2": "JunctionMerge",
                    "BaseAlign": segment_id,  # Use the respective id
                    "SketchAlign": sketch_align_value,  # Index of the group, adjust if needed
                    "JunctionMergeCount": len(center_points)
                }
            )
            features.append(new_feature)
    
        # Plot the line segments and center points
        # plot_segments_and_centers(g_jm_line, center_points, new_segments)

    print(features)  
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

    # sketch = open(Inputsketchpath)
    # sketchdata= json.load(sketch)
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
            
    # Initialize list to store coordinates for s_a2e_ids
    s_a2e_l = []
    s_a2e_p = []
  
    for sublist in s_a2e_ids_l:
        for sid in sublist:
            for feature in sketchdata['features']:
                if feature['properties']['sid'] == sid:
                    s_a2e_l.append(geometry.LineString(feature['geometry']['coordinates']))
    # breakpoint()
    
    for feature in sketchdata['features']:
        geo = feature['geometry']
        properties = feature['properties']
        sid = properties['sid']
        for sublist in s_a2e_ids_p:
            for y in sublist:
                if y == sid:
                    # breakpoint()
                    type = geo['type']
                    coor = geo['coordinates']
                    f_coor = geometry.Polygon(coor[0])
                    s_a2e_p.append(f_coor)

                
    s_a2e_l_res = []
    for sublist in s_a2e_ids:
        start = sum([len(sub) for sub in s_a2e_l_res])
        end = start + len(sublist)
        s_a2e_l_res.append(s_a2e_l[start:end])
        
    s_a2e_p_res = []
    for sublist in s_a2e_ids:
        start = sum([len(sub) for sub in s_a2e_p_res])
        end = start + len(sublist)
        s_a2e_p_res.append(s_a2e_p[start:end])
    
    # features = []
    # processed_sids = set()
    # print(s_a2e_l_res, s_a2e_ids)
    # breakpoint()
    for x, ids, sids in zip(s_a2e_l_res, a2e_ids, s_a2e_ids_l):
        multi_line = geometry.MultiLineString(x)
        # breakpoint()
        if is_connected(multi_line):
            merged_line = ops.linemerge(multi_line)
            g1_a2e = geometry.shape(merged_line)
        else:
            g1_a2e = multi_line

        # Gather properties from the sketchdata
        merged_properties = {"mapType": "Sketch"}
        for feature in sketchdata['features']:
            if feature['properties']['sid'] in sids:
                merged_properties.update(feature['properties'])
                # processed_sids.add(feature['properties']['sid'])

        features.append(Feature(geometry=geometry.mapping(g1_a2e), properties=merged_properties))
 
    # sketchdata['features'] = [feature for feature in sketchdata['features'] if feature['properties']['sid'] not in processed_sids]
    
    for x, ids, sids in zip(s_a2e_p_res, a2e_ids_p, s_a2e_ids_p):
        if len(x) == 0: # Skip empty inputs
            continue
        # breakpoint()
        mpt = geometry.MultiPolygon(x)
        res = mpt.convex_hull.wkt
        g1_a2e = shapely.wkt.loads(res)
        
        # Gather properties from the sketchdata
        merged_properties = {"mapType": "Sketch"}
        for feature in sketchdata['features']:
            if feature['properties']['sid'] in sids:
                merged_properties.update(feature['properties'])
                # processed_sids.add(feature['properties']['sid'])

        features.append(Feature(geometry=geometry.mapping(g1_a2e), properties=merged_properties))
        
     
    # Assuming you have two feature collections, feature_collection1 and feature_collection2
    combined_feature_collection = {
        "type": "FeatureCollection",
        "features": []
    }
    # Append the features from feature_collection1 to the combined feature collection
    for feature in feature_collection["features"]:
        combined_feature_collection["features"].append(feature)
    # breakpoint() 
    # Flatten s_a2e_ids to easily check if an sid is in this list
    flattened_s_a2e_ids = [sid for sublist in s_a2e_ids for sid in sublist]
    # Append the features from feature_collection2 to the combined feature collection
    for feature in sketchdata["features"]:
        if feature['properties']['sid'] not in flattened_s_a2e_ids:
            combined_feature_collection["features"].append(feature)
    
    # breakpoint()
    print(combined_feature_collection)
    align.close()
    base.close()
    sketch.close()

    outputpath =  os.path.join(USER_PROJ_DIR,"generalizedoutputMap"+".json")
    if os.path.exists(outputpath):
        os.remove(outputpath)
    f = open(outputpath, "a+")
    f.write(json.dumps(combined_feature_collection,indent=4))
    f.close()
    
    return(json.dumps(combined_feature_collection,indent=4))




