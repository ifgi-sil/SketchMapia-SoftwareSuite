from django.shortcuts import render
import os
import json
from django.http import HttpResponse
from django.template import loader
from . import qualitativeAnalyser
from qualifier import qualify_map

#@app.route("/mmReceiver", methods=["POST", "GET"])
def mmGeoJsonReceiver(request):
    # template = loader.get_template('../templates/generalizingmaps.html')
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
    # print(MetricMap_QCNS)
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
    # template = loader.get_template('../templates/generalizingmaps.html')
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


# Create your views here.
def analyzeQualitative(request):
    sketchFileName = str(request.POST.get('sketchFileName'))
    metricFileName = str(request.POST.get('metricFileName'))
    metricMapQCNs = json.loads(sketchFileName)
    sketchMapQCNs = json.loads(metricFileName)
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

    qualitative_results = {
        "sketchMapID": sketchFileName,
        "totalRCC11Relations_mm": totalRCC11Relations_mm,
        "totalRCC11Relations": totalRCC11Relations,
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
        "f_score": "nil"
    }
    # breakpoint()
    print(qualitative_results)

    return HttpResponse(json.dumps(qualitative_results), content_type="application/json")
