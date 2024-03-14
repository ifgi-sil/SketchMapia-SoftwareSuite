# -*- coding: utf-8 -*-
"""
Created on Fri Feb 02 14:02:12 2018
  -Computes linear ordering betweeen adjacent landmarks and street

@author: s_jan001
"""
from qualifier.utils_i4l import computeMinMaxDist, computeAdjacency,linear_referencing,get_defined_route
from shapely.geometry import Point,LineString


def linear_ordering (geom1, geom2):
    #coordint = geom1.coords[:]
    #print coordint
    A1 = geom1['interval'][:][0]
    A2 = geom1['interval'][:][1]

    B1 = geom2['interval'][:][0]
    B2 = geom2['interval'][:][1]

    if (A1 <= A2 and B1 <= B2 and A1 < B1 and A1 < B2 and A2 < B1 and A2 < B2):
        return "before"
    elif(A1 <= A2 and B1 <= B2 and B1 < A1 and B1 < A2 and B2 < A1 and B2 < A2):
        return "after"
    elif (A1 <= A2 and B1 <= B2 and A2 == B1 and A2 < B2):
        return "meets"
    elif (A1 >= A2 and B1 >= B2 and A1 == B2 and A1 > B2):
        return "meet_by"
    elif (A1 <= A2 and B1 <= B2 and B1 < A2 and A2 < B2 ):
        return "overlaps"
    elif (A1 <= A2 and B1 <= B2 and A1 < B2 and B2 < A2):
        return "overlapped_by"
    elif (A1 <= A2 and B1 <= B2 and B1 < A1 and A2 < B2):
        return "during"
    elif (A1 <= A2 and B1 <= B2 and A1 < B1 and B2 < A2):
        return "during_inv"
    elif (A1 <= A2 and B1 <= B2 and A1 == B1 and B2 < A2):
        return "starts"
    elif (A1 <= A2 and B1 <= B2 and A1 == B1 and A2 < B2):
        return "started_by"
    elif (A1 <= A2 and B1 <= B2 and B1 < A2 and A2 == B2):
        return "finishes"
    elif (A1 <= A2 and B1 <= B2 and A1 < B2 and A2 == B2):
        return "finished_by"
    elif (A1 <= A2 and B1 <= B2 and A1 == B1 and A2 == B2):
        return "equals"

   
def qualify_linear_ordering(data):
    relation_set = 'linearOrdering'
    arity = 2
    polygonList = []
    streetList = []
    poly_Intervals_list = []
    street_Intervals_list = []
    intervalList=[]
    polyIDList = []
    streetIDList = []
    
    for i in range(len(data)):
        if(data[i]['geometry'].geom_type=='Polygon'):
            polygonList.append((i, data[i]['geometry']))
        elif(data[i]['geometry'].geom_type=='LineString'):
            streetList.append((i, data[i]['geometry']))

    maxMinDist = computeMinMaxDist(polygonList, streetList)
    print(maxMinDist)
    defined_route = get_defined_route(data)
    #print(defined_route)
    for i in range(len(data)):
        for sec in data:
            if (data[i]['geometry'].geom_type=='Polygon'and sec['geometry'].geom_type=='LineString' and sec['attributes']['isRoute']=='Yes'):
                #check that the two geoms are adjacent 
                isAdjacent= computeAdjacency(data[i]['geometry'], defined_route,maxMinDist)
                #print("adjacent...",isAdjacent)
                if(isAdjacent == "Adjacent"):
                    #project and extract intervals of adjacent landmarks
                    intA, intB = linear_referencing(data[i]['geometry'], defined_route)
                    interval = {"interval":[intA, intB]}

                    if data[i] not in polyIDList:
                        polyIDList.append(data[i])         
                        #poly_Intervals_list.append((data[i], LineString([intA, intB])))
                        #print("object intervals ....",(data[i], interval))
                        poly_Intervals_list.append((data[i], interval))
                        #print(poly_Intervals_list)
                    if sec not in streetIDList:
                        streetIDList.append(sec) 
                        street_Intervals_list.append((sec,sec['geometry']))
                         
   # intervalList.extend(street_Intervals_list)
    intervalList.extend(poly_Intervals_list)

    return relation_set, arity, {},[{'obj 1':intervalList[i][0]['attributes']['id'], 'obj 2':sec[0]['attributes']['id'], 'relation':linear_ordering(intervalList[i][1], sec[1])} 
        for i in range(len(intervalList[:-1])) for sec in intervalList[i+1:] ]
