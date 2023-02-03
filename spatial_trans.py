
import json
from shapely import geometry, ops
from matplotlib import pyplot as plt
import shapely.wkt
import geopandas as gpd
import pandas as pd
from math import sqrt
import os
import geojson
from geojson import Feature, Point, FeatureCollection, Polygon, dump

def spatial_transformation ():
    USER_PROJ_DIR = "generalizedMap"
    Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
    Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
    Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
    f = open(Inputbasepath)
    g = open(Inputsketchpath)
    h = open(Inputaligndata)

    # returns JSON object as a dictionary
    data = json.load(h)
    amal_ids = []
    ng_ids = []
    om_ids=[]
    c_ids =[]
    for k,v in data.items():
        for val,val1 in v.items():
            key = 'genType'
            try:
                if val1[key] == 'Amalgamation':
                    id = val1['BaseAlign']['0']
                    amal_ids.append(id)
                if val1[key] == "No generalization":
                    ng_id = val1['BaseAlign']['0']
                    ng_ids.append(ng_id)

                if val1[key]== "Omission_merge":
                    om_id = val1['BaseAlign']['0']
                    om_ids.append(om_id)

                if val1[key]== "Collapse":
                    c_id = val1['BaseAlign']['0']
                    c_ids.append(c_id)

            except (KeyError,TypeError) as error:
                continue
    h.close()
    
    data_ip = json.load(f)
    poly = []
    line = []
    point = []
    no_gen = []
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
                    f_coor = geometry.LineString(coor)
                    no_gen.append(f_coor)
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
    f.close()
    
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

    ng_res = []
    for sublist in ng_ids:
        start = sum([len(sub) for sub in ng_res])
        end = start + len(sublist)
        ng_res.append(no_gen[start:end])

    features = []
    # amalgamation 
    for x in poly_res:
        mpt = geometry.MultiPolygon(x)
        res = mpt.convex_hull.wkt
        g1_a = shapely.wkt.loads(res)
        features.append(Feature(geometry=g1_a, properties={"genType": "Amalgamation"}))

    # omission_merge
    # for x in line:
        # multi_line = geometry.MultiLineString(line)
        # merged_line = ops.linemerge(multi_line)
        # g1_o = shapely.wkt.loads(str(merged_line))
        # features.append(Feature(geometry=g1_o, properties={"genType": "Omission_merge"}))

    # collapse
    for x in point_res:
        collapse = x[0].centroid
        g1_c = shapely.wkt.loads(str(collapse))
        features.append(Feature(geometry=g1_c, properties={"genType": "Collapse"}))
 
    # No Generalization
    for x in ng_res:
        multi_line = geometry.LineString(x[0])
        g1_n = shapely.wkt.loads(str(multi_line))
        features.append(Feature(geometry=g1_n, properties={"genType": "No generalization"}))

    feature_collection = FeatureCollection(features)
    
    with open('outputbaseMap.json', 'w') as f:
        dump(feature_collection, f)


    # Network flow
    # nf_id = [[7,8,9]]
    # ls=[]
    # for i in data_ip['features']:
    #     geo = i['geometry']
    #     properties = i['properties']
    #     id = properties['id']
    #     for x in nf_id:
    #         for y in x:
    #             if y == id :
    #                 type = geo['type']
    #                 coor = geo['coordinates']
    #                 ls.append(coor)
    #             else:
    #                 continue

    # def joinSegments( s ):
    #     if s[0][0] == s[1][0] or s[0][0] == s[1][-1]:
    #         s[0].reverse()
    #     c = s[0][:]
    #     for x in s[1:]:
    #         if x[-1] == c[-1]:
    #             x.reverse()
    #         c += x
    #     return c

    # res = joinSegments(ls)

    # def split_list(Input_list, n):
    #     for i in range(0, len(Input_list), n):
    #         yield Input_list[i:i + n]
    # n = 2
    # val=split_list(res, n)
    # co_or=list(val)

    # f_out=dict(zip(nf_id[0], co_or))

    # # breakpoint()
    # print(f_out)
    # return(f_out)
    return


spatial_transformation()
