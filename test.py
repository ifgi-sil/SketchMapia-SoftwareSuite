
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

# USER_PROJ_DIR = "generalizedMap"
# Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
# Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
# Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
# # breakpoint()
# # Opening JSON file
# # f = open("F:/student job/SketchMapia-SoftwareSuite/generalizedMap/inputbaseMap.json")
# # g = open("F:/student job/SketchMapia-SoftwareSuite/generalizedMap/inputsketchMap.json")
# # h = open("F:/student job/SketchMapia-SoftwareSuite/generalizedMap/alignment.json")
# f = open(Inputbasepath)
# g = open(Inputsketchpath)
# h = open(Inputaligndata)
# # returns JSON object as a dictionary
# # breakpoint()

# data = json.load(h)
# amal_ids = []
# ng_ids = []
# om_ids=[]
# c_ids =[]
# for k,v in data.items():
#     # breakpoint()
#     # print(j)
#     for val,val1 in v.items():
#         key = 'genType'
#         # value = 'Amalgamation'
#         try:
#             if val1[key] == 'Amalgamation':
#                 # print(val1['BaseAlign'])
#                 id = val1['BaseAlign']['0']
#                 amal_ids.append(id)
#             # else:
#             #     pass
#             if val1[key] == "No generalization":
#                 ng_id = val1['BaseAlign']['0']
#                 ng_ids.append(ng_id)

#             if val1[key]== "Omission_merge":
#                 om_id = val1['BaseAlign']['0']
#                 om_ids.append(om_id)

#             if val1[key]== "Collapse":
#                 c_id = val1['BaseAlign']['0']
#                 c_ids.append(c_id)

#         except (KeyError,TypeError) as error:
#             continue
#         # print(val1["genType"])
#         # for type, type1 in val1.items(): 
#         #     print(type1['genType'])
# # breakpoint()
# print(amal_ids)
# print(c_ids)
# print(ng_ids)
# h.close()

# data_ip = json.load(f)
# poly = []
# line = []
# point = []
# no_gen = []
# for i in data_ip['features']:
#     geo = i['geometry']
#     properties = i['properties']
#     id = properties['id']
#     # a =[]
#     for x in amal_ids:
#         # breakpoint()
#         for y in x:
#             a = []
#             if y == id :
#                 # print(id)
#                 type = geo['type']
#                 coor = geo['coordinates']
#                 # breakpoint()
#                 # print(coor)
#                 f_coor = geometry.Polygon(coor[0])
#                 poly.append(f_coor)
#                 # if y in x:
#                 #     a.append(f_coor)
                
#             else:
#                 continue
#             # poly.append(a)
#     for x in om_ids:
#         for y in x:
#             if y == id :
#                 type = geo['type']
#                 coor = geo['coordinates']
#                 # breakpoint()
#                 # print(coor)
#                 f_coor = geometry.LineString(coor)
#                 line.append(f_coor)
#             else:
#                 continue

#     for x in ng_ids:
#         for y in x:
#             if y == id :
#                 type = geo['type']
#                 coor = geo['coordinates']
#                 # breakpoint()
#                 # print(coor)
#                 f_coor = geometry.LineString(coor)
#                 no_gen.append(f_coor)
#             else:
#                 continue

#     for x in c_ids:
#         for y in x:
#             if y == id :
#                 type = geo['type']
#                 coor = geo['coordinates']
#                 # breakpoint()
#                 # print(coor)
#                 f_coor = geometry.Polygon(coor[0])
#                 point.append(f_coor)
#             else:
#                 continue
#     # print(coor)
#     #for j in i['geometry']:
#         #type = j['type']
#     # poly.append(a)
# # breakpoint()
# print(poly)
# # print(line)
# print(point)
# print(no_gen)
# poly_res = []
# for sublist in amal_ids:
#     start = sum([len(sub) for sub in poly_res])
#     end = start + len(sublist)
#     poly_res.append(poly[start:end])
# # breakpoint()

# point_res = []
# for sublist in c_ids:
#     start = sum([len(sub) for sub in point_res])
#     end = start + len(sublist)
#     point_res.append(point[start:end])

# ng_res = []
# for sublist in ng_ids:
#     start = sum([len(sub) for sub in ng_res])
#     end = start + len(sublist)
#     ng_res.append(no_gen[start:end])

# print(poly_res)
# print(point_res)
# print(ng_res)


# f.close()


# # def amalgamation (polygons):
#     # merged_polygon = gpd.GeoSeries(ops.unary_union(polygons))
#     # breakpoint()
# # mpt = geometry.MultiPolygon(poly)
# # res = mpt.convex_hull.wkt
#     # print(res)
#     # res1= gpd.GeoSeries(pd.Series(res).apply(shapely.wkt.loads))
#     # res1.plot()
#     # plt.show()
# # g1_a = shapely.wkt.loads(res)
# # g_amal = geojson.Feature(geometry=g1_a, properties={"genType": "Amalgamation"})
#     # return (g_amal)


# # def omission_merge(line):
# # multi_line = geometry.MultiLineString(line)
# # merged_line = ops.linemerge(multi_line)
#     # gs_ls = gpd.GeoSeries(pd.Series([str(merged_line)]).apply(shapely.wkt.loads))
#     # gs_ls.plot()
# # g1_o = shapely.wkt.loads(str(merged_line))
# # g_omimerge = geojson.Feature(geometry=g1_o, properties={"genType": "Omission_merge"})
#     # return(g_omimerge)
    

# # def collapse(polygon):
# # collapse = point[0].centroid
#     # gs_p = gpd.GeoSeries(pd.Series([str(collapse)]).apply(shapely.wkt.loads))
# #     # gs_p.plot()
# # g1_c = shapely.wkt.loads(str(collapse))
# # g_collapse = geojson.Feature(geometry=g1_c, properties={"genType": "Collapse"})
#     # return (g_collapse)

# # try:
# #     
# # except IndexError:
# #         pass

# # amalgamation(poly)
# # breakpoint()
# # omission_merge(line)
# # collapse(point[0])

# # g_no_gen = geojson.Feature(geometry=g1_n, properties={"genType": "No generalization"})

# # mpt = geometry.MultiPolygon(poly)
# # res = mpt.convex_hull.wkt
# # g1_a = shapely.wkt.loads(res)
# # g_amal = geojson.Feature(geometry=g1_a, properties={"genType": "Amalgamation"})


# features = []
# # breakpoint()
# # amalgamation 
# for x in poly_res:
#     mpt = geometry.MultiPolygon(x)
#     res = mpt.convex_hull.wkt
#     g1_a = shapely.wkt.loads(res)
#     features.append(Feature(geometry=g1_a, properties={"genType": "Amalgamation"}))

# # omission_merge
# # for x in line:
#     # multi_line = geometry.MultiLineString(line)
#     # merged_line = ops.linemerge(multi_line)
#     # g1_o = shapely.wkt.loads(str(merged_line))
#     # features.append(Feature(geometry=g1_o, properties={"genType": "Omission_merge"}))

# # breakpoint()
# # collapse
# for x in point_res:
#     collapse = x[0].centroid
#     g1_c = shapely.wkt.loads(str(collapse))
#     features.append(Feature(geometry=g1_c, properties={"genType": "Collapse"}))
 
# breakpoint()   
# # No Generalization
# for x in ng_res:
#     multi_line = geometry.LineString(x[0])
#     g1_n = shapely.wkt.loads(str(multi_line))
#     features.append(Feature(geometry=g1_n, properties={"genType": "No generalization"}))


# # json_object = json.dumps(g_amal)
# # # json_object1 = json.dumps((omission_merge(line)), indent=4)
# # json_object2 = json.dumps(collapse(point[0]))
# # json_object3 = json.dumps(g_no_gen)
# # features.append(json_object)
# # # features.append(json_object1)
# # features.append(json_object2)
# # features.append(json_object3)
# feature_collection = FeatureCollection(features)

# with open('outputbaseMap.json', 'w') as f:
#    dump(feature_collection, f)

# # with open("outputbaseMap.json", "w") as outfile:
# #     outfile.write(json_object)
# #     # outfile.write(json_object1)
# #     outfile.write(json_object2)
# #     outfile.write(json_object3)

# breakpoint()




# # Network flow
# nf_id = [[7,8,9]]
# ls=[]
# # sh_ls=[]
# for i in data_ip['features']:
#     geo = i['geometry']
#     properties = i['properties']
#     id = properties['id']
#     for x in nf_id:
#         for y in x:
#             if y == id :
#                 type = geo['type']
#                 coor = geo['coordinates']
#                 # breakpoint()
#                 # print(coor)
#                 # f_coor = geometry.LineString(coor)
#                 # sh_ls.append(f_coor)
#                 ls.append(coor)
#             else:
#                 continue

# # breakpoint()

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

# breakpoint()
# print(f_out)


# # import shapely.wkt
# # import shapely.ops

# # def reverse_geom(geom):
# #     def _reverse(x, y, z=None):
# #         if z:
# #             return x[::-1], y[::-1], z[::-1]
# #         return x[::-1], y[::-1]

# #     return shapely.ops.transform(_reverse, geom)
# # print(reverse_geom(ls[-1]))

# ## Omission merge
# line_a = geometry.LineString([[264.077892, 408.611908], [426.125329, 538.589229]])
# line_b = geometry.LineString([[426.125329, 538.589229], [456.134114, 455.603709]])
# multi_line = geometry.MultiLineString([line_a, line_b])
# merged_line = ops.linemerge(multi_line)
# # print(merged_line)

# ## Collapse
# polygon_a = geometry.Polygon([[158.046852, 285.633366], [205.060615, 325.626388], [234.069107, 238.641566], [180.053294, 198.648544], [158.046852, 285.633366]])
# polygon_b = geometry.Polygon([[238.070278, 290.632494], [246.072621, 353.621503], [319.093997, 304.630051], [299.088141, 234.642263], [238.070278, 290.632494]])
# collapse = polygon_a.centroid
# collapse1 = polygon_b.centroid
# # print(collapse,collapse1)

# # Plotting 
# line_string = [str(merged_line)]
# point = [str(collapse),str(collapse1)]
# # line_string = ["LINESTRING (264.077892 408.611908, 426.125329 538.589229, 456.134114 455.603709)"]
# # point = ["POINT (194.7643216061933 261.4943867940164)", "POINT (276.92116594859226 295.7026361150586)"]
# gs_ls = gpd.GeoSeries(pd.Series(line_string).apply(shapely.wkt.loads))
# gs_p = gpd.GeoSeries(pd.Series(point).apply(shapely.wkt.loads))
# ax = gs_ls.plot()
# ax = gs_p.plot(ax=ax)
# # plt.show()


# ## Amalgamation
# polygon_c = geometry.Polygon([[304.089605, 203.647672], [348.102489, 273.63546], [386.113616, 223.644182], [331.097511, 149.657092], [304.089605, 203.647672]])
# polygon_d = geometry.Polygon([[206.060908, 168.653778], [253.074671, 245.640344], [285.084041, 196.648893], [253.074671, 123.661628], [206.060908, 168.653778]])
# polygons = [polygon_a, polygon_b, polygon_c, polygon_d]
# breakpoint()
# merged_polygon = gpd.GeoSeries(ops.unary_union(polygons))
# merged_polygon = gpd.GeoSeries(ops.cascaded_union(polygons))
# # print(merged_polygon)
# merged_polygon.plot(color = 'red')
# plt.show()

# mpt = geometry.MultiPolygon(polygons)
# res = mpt.convex_hull.wkt
# res1= gpd.GeoSeries(pd.Series(res).apply(shapely.wkt.loads))
# res1.plot()
# plt.show()

# #  other ways
# # line = LineString([(0, 0), (1, 1), (2, 2)])
# # endpoints = line.boundary
# # print(endpoints)
# # MULTIPOINT (0 0, 2 2)
# # first, last = line.boundary
# # print(first, last)
# # POINT (0 0) POINT (2 2)

# #  or 
# # first = Point(line.coords[0])
# # last = Point(line.coords[-1])
# # print(first, last)


# # https://www.google.com/search?q=how+to+define+start+and+end+in+network+with+list+of+linestring+in+python&rlz=1C1CHWL_enIN995IN995&ei=xxt9Y6i-OLGXxc8P_I-SiAY&ved=0ahUKEwjovZ2JvML7AhWxS_EDHfyHBGEQ4dUDCBA&uact=5&oq=how+to+define+start+and+end+in+network+with+list+of+linestring+in+python&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzoKCAAQRxDWBBCwAzoICCEQwwQQoAE6CgghEMMEEAoQoAE6BQgAEKIEOgcIABAeEKIEOgQIIRAKSgQIQRgASgQIRhgAUJUFWMhqYNlyaAFwAXgAgAG1AogBpiySAQg2LjIxLjguMZgBAKABAcgBCMABAQ&sclient=gws-wiz-serp
# # https://gis.stackexchange.com/questions/415864/how-do-you-flip-invert-reverse-the-order-of-the-coordinates-of-shapely-geometrie

# #Line in one direction


# # def to_square(polygon):
    
# #     minx, miny, maxx, maxy = polygon.bounds
    
# #     # get the centroid
# #     centroid = [(maxx+minx)/2, (maxy+miny)/2]
# #     # get the diagonal
# #     diagonal = sqrt((maxx-minx)**2+(maxy-miny)**2)
    
# #     return geometry.Point(centroid).buffer(diagonal/sqrt(2.)/2., cap_style=3)

# # m = to_square(polygons)
# # m.plot()
# # plt.show()







# # with open('path_to_file/person.json', 'r') as f:
# #  data = json.load(f)


# # files = glob.glob('data/*', recursive=True)

# # for single_file in files:
# #   with open(single_file, 'r') as f:

# #     try:
# #       json_file = json.load(f)
# #       data.append([
# #         json_file['score'],
# #         json_file['otherValue']
# #       ])
# #     except KeyError:
# #       print(f'Skipping {single_file}')

# # data.sort()

# # data.insert(0, ['fileName','score','otherValue'])

# # print(data)



# # import fme
# # import fmeobjects


# # function generalizeMap(){
# # //console.log(AlignmentArray)
# # var lastBaseStreet = routeArray[routeArray.length - 1];
# # //var alignment = JSON.stringify(AlignmentArray);
# # //alignjson= JSON.stringify(AlignmentArray.toGeoJSON())
# # //console.log(alignment)
# # if (routeArray.length == 0){
# #   drawnItems.eachLayer(function(blayer){
# #            if (blayer.feature.properties.isRoute == "Yes"){
# #               routeArray.push(blayer.feature.properties.id);
# #   }
# #  });
# # }
# # lastBaseStreet = routeArray[routeArray.length - 1];
# # var lastSketchStreet = sketchRouteArray[sketchRouteArray.length -1];

# # var url = "http://desktop-f25rpfv:8080/fmedatastreaming/Generalization/generalizerFile.fmw?Alignment=" + encodeURIComponent(JSON.stringify(JSON.stringify(AlignmentArray))) + "&RouteSeq=" + encodeURIComponent(routeArray) + "&SketchRouteSeq=" + encodeURIComponent(sketchRouteArray) + "&lastsegment=" + encodeURIComponent(lastBaseStreet) + "&lastsketchsegment=" + encodeURIComponent(lastSketchStreet);
# # var newurl = "http://desktop-f25rpfv:8080/fmerest/v3/repositories/GeneralizationPredict/networkcalculator.fmw/parameters?fmetoken=47e241ca547e14ab6ea961aef083f8a4cbe6dfe3"

# #  $.ajax({
# #                 headers: { "X-CSRFToken": $.cookie("csrftoken") },
# #                 url: 'requestFME/',
# #                 type: 'POST',
# #                 data: {
# #                     basedata: JSON.stringify(drawnItems.toGeoJSON()),
# #                     sketchdata: JSON.stringify(drawnSketchItems.toGeoJSON())
# #                 },
# #                 //contentType: 'text/plain',
# #                 success: function (resp) {
# #                    console.log("Test done");
# #                    var httpRequest = new XMLHttpRequest();
# #                     httpRequest.open("GET", url, false);
# #                     httpRequest.setRequestHeader("Authorization","fmetoken token=c1f02207ac3b1489be2c18ee26cefb643d646bce")
# #                     httpRequest.setRequestHeader("Access-Control-Allow-Origin", "http://desktop-f25rpfv:8080");
# #                     httpRequest.setRequestHeader("Accept","text/html");
# #                     httpRequest.setRequestHeader("content-Type","multipart/form-data");
# #             httpRequest.onreadystatechange = function()
# #             {
# #                 if (httpRequest.readyState == 4 && httpRequest.status == 200)
# #                 {

# #                 var randomnum = 110111;
# #                 var wholeMapProc = JSON.parse(httpRequest.response);
# #                 var sketchMapProc=[];
# #                 var baseMapProc=[];
# #                  $.each(wholeMapProc.features, function(i, item) {
# #                  if(item.properties.mapType == "Sketch"){
# #                     sketchMapProc.push(item);
# #                  }
# #                  else{

# #                   if (item.properties.missing){
# #                   item.properties.id = randomnum;
# #                   }
# #                    if (item.properties.SketchAlign){
# #                     item.properties.id = Object.values(JSON.parse(item.properties.SketchAlign))[0][0].replace(/\D/g,'');
# #                  }
# #                   baseMapProc.push(item);
# #                   randomnum = randomnum + 1;
# #                  }
# #                  });


# #                 GenBaseMap = L.geoJSON(baseMapProc);

# #                 layerGroupBasemap.addLayer(GenBaseMap);
# #                 ProcSketchMap = L.geoJSON(sketchMapProc);
# #                 analyzeInputMap();
# #                 }
# #             }
# #             // send a request so we get a reply
# #             httpRequest.send();

# #                 }
# #             });

# # /*

# # */

# # }

# # def requestFME(request):
# #     template = loader.get_template('../templates/generalizingmaps.html')
# #     if request.is_ajax():
# #         basedata = request.POST.get('basedata')
# #         sketchdata = request.POST.get('sketchdata')
# #         #aligndata = request.POST.get('aligndata')
# #         #response = requests.get('http://desktop-f25rpfv:8080/fmedatastreaming/Generalization/generalizer.fmw?', params=query)
# #     USER_PROJ_DIR = "generalizedMap"
# #     baseMapdata = json.loads(basedata)
# #     sketchMapdata = json.loads(sketchdata)
# #     #breakpoint()
# #     #alignMapdata = json.loads(aligndata)
# #     try:
# #         Inputbasepath = os.path.join(USER_PROJ_DIR,"inputbaseMap"+".json")
# #         Inputsketchpath = os.path.join(USER_PROJ_DIR,"inputsketchMap"+".json")
# #         Inputaligndata =  os.path.join(USER_PROJ_DIR,"alignment"+".json")
# #         if os.path.exists(Inputbasepath):
# #             os.remove(Inputbasepath)
# #         f = open(Inputbasepath, "a+")
# #         f.write(json.dumps(baseMapdata,indent=4))
# #         f.close()

# #         if os.path.exists(Inputsketchpath):
# #             os.remove(Inputsketchpath)
# #         f = open(Inputsketchpath, "a+")
# #         f.write(json.dumps(sketchMapdata,indent=4))
# #         f.close()

# #         #if os.path.exists(Inputaligndata):
# #             #os.remove(Inputaligndata)
# #         #f = open(Inputaligndata, "a+")
# #         #f.write(json.dumps(alignMapdata,indent=4))
# #         #f.close()
# #     except IOError:
# #         print("Files written")
# #     return HttpResponse(template.render({}, request))


routedata = [{"id":0,"isRoute":"Yes","feat_type":null,"selected":false,"aligned":true,"otype":"Line","RouteSeqOrder":1},{"id":2,"isRoute":"Yes","feat_type":null,"selected":false,"aligned":true,"otype":"Line","RouteSeqOrder":2}]
nf_id = []
breakpoint()
for route in routedata:
    ids = route['id']
    nf_id.append(ids)