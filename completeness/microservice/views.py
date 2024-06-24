import os
import json
from django.shortcuts import render
from django.http import HttpResponse



def get_landmarkCompleteness(totalSketchedLandmarks,total_mm_landmark):
    if totalSketchedLandmarks != 0 or total_mm_landmark != 0:
        landmarkCompleteness = (totalSketchedLandmarks / total_mm_landmark) * 100
    else:
        landmarkCompleteness = 0.00
    return landmarkCompleteness


# get stree_completness
def get_streetCompleteness(totalSketchedStreets,toal_mm_streets):
    if totalSketchedStreets != 0 or toal_mm_streets != 0:
        streetCompleteness = (totalSketchedStreets / toal_mm_streets) * 100
    else:
        streetCompleteness = 0.00
    return streetCompleteness

# get cityblock_completeness
def get_cityblockCompleteness(totalSketchedCityblocks,total_mm_cityblocks):
    if totalSketchedCityblocks != 0 or total_mm_cityblocks != 0:
        cityblockCompleteness = (totalSketchedCityblocks / total_mm_cityblocks) * 100
    else:
        cityblockCompleteness = 0.00
    return cityblockCompleteness

# get overall accuracy
def get_overall_completness(landmarkCompleteness,streetCompleteness,cityblockCompleteness):
    overAllCompleteness = 0.00
    if(landmarkCompleteness == 0 and streetCompleteness == 0 and cityblockCompleteness == 0):
        overAllCompleteness = 0.00
    elif(landmarkCompleteness !=0 and streetCompleteness !=0 and cityblockCompleteness == 0 ):
        overAllCompleteness = (landmarkCompleteness + streetCompleteness ) / 2

    elif(landmarkCompleteness !=0 and streetCompleteness ==0 and cityblockCompleteness != 0 ):
        overAllCompleteness = (landmarkCompleteness + cityblockCompleteness) / 2

    elif (landmarkCompleteness == 0 and streetCompleteness != 0 and cityblockCompleteness != 0):
        overAllCompleteness = (streetCompleteness + cityblockCompleteness) / 2

    elif (landmarkCompleteness != 0 and streetCompleteness != 0 and cityblockCompleteness != 0):
        overAllCompleteness = (landmarkCompleteness + streetCompleteness + cityblockCompleteness) / 3

    return overAllCompleteness



def get_cityblocks_mm(mmqcns):
    cb_count=0
    if  mmqcns['properties']['map_type'] == "metric_map":
        for feature in mmqcns['features']:
            if feature['feat_type'] =="Cityblock":
                cb_count+= 1
    return cb_count


def get_streets_mm(mmqcns):
    st_count=0
    if  mmqcns['properties']['map_type'] == "metric_map":
        for feature in mmqcns['features']:
            if feature['geometry_type'] =="LineString":
                st_count+=1
    return st_count

def get_landmarks_mm(mmqcns):
    lm_count=0
    if  mmqcns['properties']['map_type'] == "metric_map":
        for feature in mmqcns['features']:
            #print(feature)
            if feature['feat_type'] =="Landmark":
                lm_count+=1

    return lm_count


"""
    get number of drawn cityblocks 
    
"""

def get_cityblocks_sm(smqcns):
    cb_count=0
    if  smqcns['properties']['map_type'] == "sketch_map":
        for feature in smqcns['features']:
            if feature['feat_type'] =="Cityblock":
                cb_count+= 1
    return cb_count

"""
    - get total number of drawn street segments
"""
def get_streets_sm(smqcns):
    st_count=0
    if  smqcns['properties']['map_type'] == "sketch_map":
        for feature in smqcns['features']:
            if feature['geometry_type'] =="LineString":
                st_count+=1
    return st_count

"""
    - get total number of drawn landmarks
"""
def get_landmarks_sm(smqcns):
    lm_count=0
    if  smqcns['properties']['map_type'] == "sketch_map":
        for feature in smqcns['features']:
            #print(feature)
            if feature['feat_type'] =="Landmark":
                lm_count+=1

    return lm_count


def analyzeCompleteness(request):
    sketchFileName = request.POST.get('sketchFileName')
    metricFileName = request.POST.get('metricFileName')
    metricMapQCNs = json.loads(sketchFileName)
    sketchMapQCNs = json.loads(metricFileName)
    
    total_mm_landmarks = get_landmarks_mm(metricMapQCNs)
    total_mm_streets = get_streets_mm(metricMapQCNs)
    total_mm_cityblocks = get_cityblocks_mm(metricMapQCNs)

    totalSketchedLandmarks = get_landmarks_sm(sketchMapQCNs)
    totalSketchedStreets = get_streets_sm(sketchMapQCNs)
    totalSketchedCityblocks = get_cityblocks_sm(sketchMapQCNs)

    landmarkCompleteness = get_landmarkCompleteness(totalSketchedLandmarks, total_mm_landmarks)
    landmarkCompleteness = round(landmarkCompleteness, 2)

    streetCompleteness = get_streetCompleteness(totalSketchedStreets, total_mm_streets)
    streetCompleteness = round(streetCompleteness, 2)

    cityblockCompleteness = get_cityblockCompleteness(totalSketchedCityblocks, total_mm_cityblocks)
    cityblockCompleteness = round(cityblockCompleteness, 2)

    overAllCompleteness = get_overall_completness(landmarkCompleteness, streetCompleteness, cityblockCompleteness)

    completeness_results = {
        "sketchMapID": "sketchmap",
        "total_mm_landmarks": total_mm_landmarks,
        "total_mm_streets": total_mm_streets,
        "total_mm_cityblocks": total_mm_cityblocks,
        "totalSketchedLandmarks": totalSketchedLandmarks,
        "totalSketchedStreets": totalSketchedStreets,
        "totalSketchedCityblocks": totalSketchedCityblocks,
        "landmarkCompleteness": landmarkCompleteness,
        "streetCompleteness": streetCompleteness,
        "cityblockCompleteness": cityblockCompleteness,
        "overAllCompleteness": round(overAllCompleteness, 2)
    }
    # breakpoint()
    print(completeness_results)
    return HttpResponse(json.dumps(completeness_results), content_type="application/json")
