from django.shortcuts import render
from django.template import loader
from django.http.response import HttpResponse
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


def omission_deadendstreets(request):
    template = loader.get_template('../templates/generalizingmaps.html')
    global G
    G2 = G.copy()

    culdesacs = [key for key, value in utils_graph.count_streets_per_node(G).items() if value == 1]
    G2.remove_nodes_from(culdesacs)
    ox.save_graph_geojson(G2, filepath='static/geojson_files/streetnetwork_simplified_deadend')
    return HttpResponse(template.render({}, request))
