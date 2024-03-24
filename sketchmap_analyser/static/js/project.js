var GenBaseMap;
var ProcSketchMap;
var StreetGroup;
var BuildingGroup;
var extraFeaturesCount = 0;
var extraFeaturesIds = [];
var missingFeaturesCount = 0;
var missingFeaturesIds = [];
var routeArray = [];
var sketchRouteArray = [];
var roundaboutcount = 0;
var junctionmergecount = 0;
var multiOmiMergeCount = 0;
var roundaboutids = [];
var junctionmergeids = [];
var qualRelationsBaseMap;
var qualRelationsSketchMap;
var multiOmiMergeids = [];
var TemporaryAlignmentArray={};






function uploadProject(){
     var fileList = document.getElementById('upload').files;
    for (var i = 0; i < fileList.length; i++) {
        renderGeoJsonFiles(fileList[i], map);
    }
}

function renderGeoJsonFiles(file, map) {
    var fileName = file.name;
    var reader = new FileReader();
    reader.readAsDataURL(file);
    if (fileName.includes('alignment')){
    reader.onload = function () {
        $.getJSON(reader.result, function (data) {
          AlignmentArray = data;
        });
    }}

    if (fileName.includes('basemap')){
    reader.onload = function () {
        $.getJSON(reader.result, function (data) {
         var bidArray = Object.values(data.features).map((item) => item.properties.id);
         var RouteSeqOrderArray = Object.values(data.features).map((item) => item.properties.RouteSeqOrder);
         routeOrder = Math.max.apply(Math,RouteSeqOrderArray);
         bid = Math.max.apply(Math, bidArray);

           drawnItems = L.geoJSON(data);
           drawnItems.addTo(layerGroupBasemap);
           allDrawnSketchItems["basemap"] = drawnItems;
            styleLayers();

           if (addedClickBase == false){
                addClickBase();
           }

        });
    }}

    if ( !(fileName.includes('basemap')) && !(fileName.includes('alignment'))){
    reader.onload = function () {
        $.getJSON(reader.result, function (data) {
         var idArray = Object.values(data.features).map((item) => item.properties.id);
         id = Math.max.apply(Math, idArray);
         sketchMaptitle = fileName.replace('.geojson','');
         drawnSketchItems =  L.geoJSON(data,{
          pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng);
          }
         });


          styleLayers();
           if (addedClickSketch == false){
                drawnSketchItems.eachLayer(function(slayer){
                slayer.off('click');
            });
            drawnSketchItems.eachLayer(function(slayer){
                 slayer.on('click', function (e) {
                    clickFunctionforSketch(e.target);
                });
            });
            }
            allDrawnSketchItems[sketchMaptitle]=drawnSketchItems;
        });
    }}
}




function downloadProject(){

 var zip = new JSZip();


 var alignment = JSON.stringify(AlignmentArray);
 zip.file("alignment.json",alignment);

 for (var key in allDrawnSketchItems) {
    zip.file(key + ".geojson", JSON.stringify(allDrawnSketchItems[key].toGeoJSON()));
}
     zip.generateAsync({type:"blob"})
        .then(function(content) {
    saveAs(content, sketchMaptitle.replace(".jpg","") + "Input.zip");

});
}

function qualify_MM(callback) {
    MMGeoJsonData = GenBaseMap.toGeoJSON();
    var count = 0;
    var MMGeoJsonDataFiltered = {};
    MMGeoJsonDataFiltered.type = "FeatureCollection";
    MMGeoJsonDataFiltered.features = [];

    for (var i in MMGeoJsonData.features){

        var group = MMGeoJsonData.features[i].properties.group;
        if(group != "Yes"){
            MMGeoJsonDataFiltered.features[count]=MMGeoJsonData.features[i];
            count = count + 1;
        }
        if(MMGeoJsonData.features[i].properties.genType3 != undefined && MMGeoJsonData.features[i].properties.genType3.includes("Multi-MultiOmissionMerge")){
            MMGeoJsonData.features[i].properties.id = 'G' + MMGeoJsonData.features[i].properties.groupID;
            MMGeoJsonDataFiltered.features[count]=MMGeoJsonData.features[i];
            count = count + 1;

        }
    }

    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8003/accuracy/mmReceiver/',
        type: 'POST',
        data:
            {
                metricFileName: "basemap",
                MMGeoJsonData: JSON.stringify(MMGeoJsonDataFiltered)
            },
        //contentType: 'application/json',
        success: function (resp) {
            console.log("Metric Map Qualify complete");
            qualRelationsBaseMap = JSON.parse(resp)
            callback(resp);
        }
    });
}

function qualify_SM(callback) {
    SMGeoJsonData = ProcSketchMap.toGeoJSON();
    var count = 0;
    var SMGeoJsonDataFiltered = {};
    var streetGroupIdÁrray = [];
    var buildingGroupIdArray = [];


    SMGeoJsonDataFiltered.type = "FeatureCollection";
    SMGeoJsonDataFiltered.features = [];
    for (var i in SMGeoJsonData.features){
        var group = SMGeoJsonData.features[i].properties.group;
        var alignBoolean = SMGeoJsonData.features[i].properties.aligned;
        if(group != "Yes" && alignBoolean == true){
            SMGeoJsonDataFiltered.features[count]= SMGeoJsonData.features[i];
            count = count + 1;
        }
        else{
           if(group == "Yes"){

           if(SMGeoJsonData.features[i].properties.genType3 != undefined && SMGeoJsonData.features[i].properties.genType3.includes("Multi-MultiOmissionMerge")){
            SMGeoJsonData.features[i].properties.id = 'G' + SMGeoJsonData.features[i].properties.groupID;
            SMGeoJsonDataFiltered.features[count]=SMGeoJsonData.features[i];
            count = count + 1;
            }
            if(SMGeoJsonData.features[i].properties.otype == "Line"){
                streetGroupIdÁrray.push(SMGeoJsonData.features[i].properties.groupID);
            }
            if(SMGeoJsonData.features[i].properties.otype == "Polygon"){
                buildingGroupIdArray.push(SMGeoJsonData.features[i].properties.groupID);
            }
           }
        }

        if(alignBoolean == false){
             extraFeaturesCount = extraFeaturesCount + 1;
             extraFeaturesIds.push(SMGeoJsonData.features[i].properties.sid);
        }
    }
    // fileName = sketchFileName.split(".");
    // fileName = fName[0];
    StreetGroup = new Set(streetGroupIdÁrray);
    BuildingGroup = new Set(buildingGroupIdArray);

    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8003/accuracy/smReceiver/',
        type: 'POST',
        data: {
            sketchFileName:"sketchmap",
            SMGeoJsonData: JSON.stringify(SMGeoJsonDataFiltered)
        },
        //dataType: 'json',
        success: function (resp) {
            console.log("Sketch Map Qualify complete");
            qualRelationsSketchMap = JSON.parse(resp)
            callback(resp);
        }
    });
}

var GenHoverArray = [];

function Genhoverfunction(){
    drawnSketchItems.eachLayer(function(slayer){
    slayer.on('mouseover', function() {
    if(slayer.feature.properties.group != true){
    GenHoverArray.push(slayer.feature.properties.id);
    GenchangestyleOnHover(GenHoverArray,slayer.feature.properties.group);
    }
    else
    {
    GenHoverArray.push(slayer.feature.properties.groupID);
    GenchangestyleOnHover(GenHoverArray,slayer.feature.properties.group);
    }
    });
    slayer.on('mouseout', function() {
    GenHoverArray=[];
    GenStyleLayers();
    });
    });
    }

function GenchangestyleOnHover(Array,BooleanGroup){
    Array=Array.flat();
    if (BooleanGroup != true){
     GenBaseMap.eachLayer(function(glayer){
     for (i in Array){
        if (glayer.feature.properties.id==Array[i]){
                glayer.setStyle({
            color: 'blue'   //or whatever style you wish to use;
        });
        }
    }

     });
     drawnSketchItems.eachLayer(function(slayer){
     for (i in Array){
        if (slayer.feature.properties.sid==Array[i]){
            slayer.setStyle({
            color: 'blue'   //or whatever style you wish to use;
        });
        }
    }
   });
   }
   else {

     GenBaseMap.eachLayer(function(glayer){
     for (i in Array){
        if (glayer.feature.properties.groupID==Array[i]){
                glayer.setStyle({
            color: 'blue'   //or whatever style you wish to use;
        });
        }
    }

     });
     drawnSketchItems.eachLayer(function(slayer){
     for (i in Array){
        if (slayer.feature.properties.groupID==Array[i]){
            slayer.setStyle({
            color: 'blue'   //or whatever style you wish to use;
        });
        }
    }
   });


   }

    }


// function generalizeMap(){
// routeArray = [];
// sketchRouteArray = [];
// missingFeaturesCount = 0;
// extraFeaturesCount = 0;
//          drawnItems.eachLayer(function(blayer){
//         if (!blayer.feature.properties.aligned ){
//             blayer.feature.properties.missing = true;
//             missingFeaturesCount = missingFeaturesCount + 1;
//             missingFeaturesIds.push(blayer.feature.properties.id);
//         }
//         else
//         {delete blayer.feature.properties.missing; }
//         });



//   drawnItems.eachLayer(function(blayer){
//            if (blayer.feature.properties.isRoute == "Yes"){
//               routeArray.push(blayer.feature.properties);
//   }
//  });


// var byrouteorder = routeArray.slice(0);
//     byrouteorder.sort(function(a,b) {
//         return a.RouteSeqOrder - b.RouteSeqOrder;
//     });





// drawnSketchItems.eachLayer(function(slayer){
//            if (slayer.feature.properties.isRoute == "Yes"){
//               sketchRouteArray.push(slayer.feature.properties);
//   }
//  });

// var bysketchrouteorder = sketchRouteArray.slice(0);
//     bysketchrouteorder.sort(function(a,b) {
//         return a.SketchRouteSeqOrder - b.SketchRouteSeqOrder;
//     });

// var routeIDArray = [];
// var sketchIDArray = [];
// for (var i in byrouteorder){
// routeIDArray.push(byrouteorder[i].id);
// }

// for (var i in bysketchrouteorder){
// sketchIDArray.push(bysketchrouteorder[i].id);
// }
// var lastSketchStreet = sketchIDArray[sketchIDArray.length -1];
// var lastBaseStreet = routeIDArray[routeIDArray.length - 1];

// AlignmentArray[sketchMaptitle]=alignmentArraySingleMap;
// AlignmentArray[sketchMaptitle].checkAlignnum = checkAlignnum;

// // console.log("route",routeIDArray);
// // var url = "http://localhost:8080/fmedatastreaming/Generalization/generalizerFile.fmw?Alignment=" + encodeURIComponent(JSON.stringify(JSON.stringify(AlignmentArray))) + "&RouteSeq=" + encodeURIComponent(routeIDArray) + "&SketchRouteSeq=" + encodeURIComponent(sketchIDArray) + "&lastsegment=" + encodeURIComponent(lastBaseStreet) + "&lastsketchsegment=" + encodeURIComponent(lastSketchStreet);
// // var newurl = "http://desktop-f25rpfv:8080/fmerest/v3/repositories/GeneralizationPredict/networkcalculator.fmw/parameters?fmetoken=47e241ca547e14ab6ea961aef083f8a4cbe6dfe3"
// // console.log("Data to be sent:", {
// //     basedata: JSON.stringify(drawnItems.toGeoJSON()),
// //     sketchdata: JSON.stringify(drawnSketchItems.toGeoJSON()),
// //     aligndata: JSON.stringify(AlignmentArray),
// //     routedata: JSON.stringify(routeArray),
// //     sketchroutedata: JSON.stringify(sketchRouteArray)
// // });
//  $.ajax({
//                 headers: { "X-CSRFToken": $.cookie("csrftoken")},
//                 url: 'http://127.0.0.1:8001/generalizations/requestFME/',
//                 // credentials: "include",
//                 type: 'POST',
//                 data: {
//                     csrfmiddlewaretoken: $.cookie("csrftoken"),
//                     basedata: JSON.stringify(drawnItems.toGeoJSON()),
//                     sketchdata: JSON.stringify(drawnSketchItems.toGeoJSON()),
//                     aligndata: JSON.stringify(AlignmentArray),
//                     routedata: JSON.stringify(routeArray),
//                     sketchroutedata: JSON.stringify(sketchRouteArray)
//                 },
//                 // contentType: 'application/json',
//                 // contentType: 'text/plain',
//                 success: function (resp) {
//                     console.log(resp)
//             //        var httpRequest = new XMLHttpRequest();
//             //         httpRequest.open("GET", url, false);
//             //         httpRequest.setRequestHeader("Authorization","fmetoken token=*****")
//             //         httpRequest.setRequestHeader("Access-Control-Allow-Origin", "http://localhost:8080");
//             //         httpRequest.setRequestHeader("Accept","text/html");
//             //         httpRequest.setRequestHeader("content-Type","multipart/form-data");
//             // httpRequest.onreadystatechange = function()
//             {
//                 // if (httpRequest.readyState == 4 && httpRequest.status == 200)
//                 // {

//                 var randomnum = 110111;
//                 var wholeMapProc = JSON.parse(resp);
//                 var sketchMapProc=[];
//                 var baseMapProc=[];
//                  multiOmiMergeCount = 0;
//                  $.each(wholeMapProc.features, function(i, item) {

//                  if(item.properties.RoundAboutCount != null ) {
//                     roundaboutcount = item.properties.RoundAboutCount;
//                  }

//                  if(item.properties.JunctionMergeCount != null ) {
//                     junctionmergecount = item.properties.JunctionMergeCount;
//                  }

//                  if(item.properties.genType2 != null && item.properties.genType2.includes("JunctionMerge")){
//                  console.log("Yes JunctionMerge")
//                     junctionmergeids.push(item.properties.id);
//                  }

//                  if (item.properties.genType3 != null && item.properties.genType3.includes("Multi-MultiOmissionMerge")){
//                     multiOmiMergeCount = multiOmiMergeCount + 1 ;
//                     multiOmiMergeids.push(item.properties.id)
//                  }
//                  if(item.properties.genType1 != null && item.properties.genType1.includes("RoundAbout")){
//                     roundaboutids.push(item.properties.id);
//                     console.log("Yes roundabout")
//                  }

//                  if(item.properties.mapType == "Sketch"){
//                       item.properties.id = item.properties.id.toString();
//                     if(item.properties.otype == "CircleMarker"){
//                         item.properties.feat_type="Landmark";
//                         }

//                     sketchMapProc.push(item);
//                  }
//                  else{
//                   if (item.properties.missing){
//                     item.properties.id = randomnum;
//                   }
//                   if (item.properties.SketchAlign){
//                     item.properties.id = Object.values(item.properties.SketchAlign)[0][0].replace(/\D/g,'');
//                   }  
//                   baseMapProc.push(item);
//                   randomnum = randomnum + 1;
//                  }
//                  });

//                 if (GenBaseMap != null) {
//                     layerGroupBasemapGen.removeLayer(GenBaseMap);
//                  }


//                 GenBaseMap = L.geoJSON(baseMapProc);
//                 GenStyleLayers();
//                 Genhoverfunction();
//                 GenBaseMap.addTo(layerGroupBasemapGen);
//                 ProcSketchMap = L.geoJSON(sketchMapProc);
//                 analyzeInputMap();
//                 }
//             }
//             // send a request so we get a reply
//             // httpRequest.send();
//             });
// }
function generalizeMap() {
    routeArray = [];
    sketchRouteArray = [];
    missingFeaturesCount = 0;
    extraFeaturesCount = 0;
    drawnItems.eachLayer(function (blayer) {
        if (!blayer.feature.properties.aligned) {
            blayer.feature.properties.missing = true;
            missingFeaturesCount = missingFeaturesCount + 1;
            missingFeaturesIds.push(blayer.feature.properties.id);
        } else {
            delete blayer.feature.properties.missing;
        }
    });

    drawnItems.eachLayer(function (blayer) {
        if (blayer.feature.properties.isRoute == "Yes") {
            routeArray.push(blayer.feature.properties);
        }
    });

    var byrouteorder = routeArray.slice(0);
    byrouteorder.sort(function (a, b) {
        return a.RouteSeqOrder - b.RouteSeqOrder;
    });

    drawnSketchItems.eachLayer(function (slayer) {
        if (slayer.feature.properties.isRoute == "Yes") {
            sketchRouteArray.push(slayer.feature.properties);
        }
    });

    var bysketchrouteorder = sketchRouteArray.slice(0);
    bysketchrouteorder.sort(function (a, b) {
        return a.SketchRouteSeqOrder - b.SketchRouteSeqOrder;
    });

    var routeIDArray = [];
    var sketchIDArray = [];
    for (var i in byrouteorder) {
        routeIDArray.push(byrouteorder[i].id);
    }

    for (var i in bysketchrouteorder) {
        sketchIDArray.push(bysketchrouteorder[i].id);
    }

    var lastSketchStreet = sketchIDArray[sketchIDArray.length - 1];
    var lastBaseStreet = routeIDArray[routeIDArray.length - 1];

    AlignmentArray[sketchMaptitle] = alignmentArraySingleMap;
    AlignmentArray[sketchMaptitle].checkAlignnum = checkAlignnum;

    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8001/generalizations/requestFME/',
        type: 'POST',
        data: {
            csrfmiddlewaretoken: $.cookie("csrftoken"),
            basedata: JSON.stringify(drawnItems.toGeoJSON()),
            sketchdata: JSON.stringify(drawnSketchItems.toGeoJSON()),
            aligndata: JSON.stringify(AlignmentArray),
            routedata: JSON.stringify(routeArray),
            sketchroutedata: JSON.stringify(sketchRouteArray)
        },
        success: function (resp) {
            // console.log(resp);
            var randomnum = 110111;
            var wholeMapProc = JSON.parse(resp);
            var sketchMapProc = [];
            var baseMapProc = [];
            multiOmiMergeCount = 0;
            $.each(wholeMapProc.features, function (i, item) {
                if(item.properties.RoundAboutCount != null ) {
                    roundaboutcount = item.properties.RoundAboutCount;
                }

                if(item.properties.JunctionMergeCount != null ) {
                    junctionmergecount = item.properties.JunctionMergeCount;
                }

                if(item.properties.genType2 != null && item.properties.genType2.includes("JunctionMerge")){
                    console.log("Yes JunctionMerge")
                    junctionmergeids.push(item.properties.id);
                }

                if (item.properties.genType3 != null && item.properties.genType3.includes("Multi-MultiOmissionMerge")){
                    multiOmiMergeCount = multiOmiMergeCount + 1 ;
                    multiOmiMergeids.push(item.properties.id)
                }
                if(item.properties.genType1 != null && item.properties.genType1.includes("RoundAbout")){
                    roundaboutids.push(item.properties.id);
                    console.log("Yes roundabout")
                }
                if(item.properties.mapType == "Sketch"){
                    item.properties.id = item.properties.id.toString();
                if(item.properties.otype == "CircleMarker"){
                    item.properties.feat_type="Landmark";
                    }
                sketchMapProc.push(item);
                }else{
                    if (item.properties.missing){
                        item.properties.id = randomnum;
                    }
                    if (item.properties.SketchAlign){
                        const sketchAlignValue = Object.values(item.properties.SketchAlign);
                        const numericPart = sketchAlignValue.toString().replace(/\D/g, ''); // Extract numeric part
                        item.properties.id = numericPart ? String(numericPart[0]) : '';
                        // item.properties.id = String(Object.values(item.properties.SketchAlign)[0][0]).replace(/\D/g,'');
                    }  
                    baseMapProc.push(item);
                    randomnum = randomnum + 1;
                }
            });
            if (GenBaseMap != null) {
                layerGroupBasemapGen.removeLayer(GenBaseMap);
            }
            GenBaseMap = L.geoJSON(baseMapProc);
            GenStyleLayers();
            Genhoverfunction();
            GenBaseMap.addTo(layerGroupBasemapGen);
            ProcSketchMap = L.geoJSON(sketchMapProc);
            // analyzeInputMap();
            var completenessPromise = analyzeCompleteness();
            var qualitativePromise = analyzeQualitative();
            
            Promise.all([completenessPromise, qualitativePromise])
                .then(function(results) {
                    var completenessData = results[0];
                    var qualitativeData = results[1];
                    handleCompletenessResults(completenessData)
                    handleCorrectnessResults(qualitativeData)
                    handlegeneralizationResults();
                    $('#summary_result_div').prop("style", " height:100%; overflow-y: scroll;  visibility: visible; position:absolute ; z-index:10000000; background-color: white");
                    $("#stepper_analyze_map").prop("style", "background: #17a2b8");
                })
                .catch(function(error) {
                    console.error('Error in fetching completeness and/or qualitative data:', error);
                });

            $(document).on('keydown', function (e) {
                if (e.keyCode === 27) { // ESC
                    $("#summary_result_div").hide();
                }
            });
        }
    });
}


function GenStyleLayers(){

GenBaseMap.eachLayer(function(glayer){
            if (!glayer.feature.properties.selected && glayer.feature.properties.missing == true && !glayer.feature.properties.isRoute){
                glayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: [5, 5]});
            }
            if (!glayer.feature.properties.selected && !glayer.feature.properties.missing && !glayer.feature.properties.isRoute){
                glayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: null});
            }
            if (!glayer.feature.properties.selected && glayer.feature.properties.missing == true && glayer.feature.properties.isRoute=="Yes"){
                glayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: [5, 5]});
            }
            if(!glayer.feature.properties.selected && !glayer.feature.properties.missing && glayer.feature.properties.isRoute=="Yes"){
                glayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: null,});
            }
     });

}

function analyzeCompleteness() {
    return new Promise(function(resolve, reject) {
        TemporaryAlignmentArray = JSON.parse(JSON.stringify(AlignmentArray));
        qualify_MM(function(resp_mm) {
            console.log("call qualify SM function");
            qualify_SM(function(resp_sm) {
                $.ajax({
                    headers: { "X-CSRFToken": $.cookie("csrftoken") },
                    url: 'http://127.0.0.1:8002/completeness/analyzeCompleteness/',
                    type: 'POST',
                    data: {
                        sketchFileName: resp_mm,
                        metricFileName: resp_sm
                    },
                    success: function(response) {
                        // console.log('completeness results:', response);
                        resolve(response); // Resolve the promise with the response data
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error('Error in completeness analysis:', errorThrown);
                        reject(errorThrown); // Reject the promise with the error message
                    }
                });
            });
        });
    });
}

function analyzeQualitative() {
    return new Promise(function(resolve, reject) {
        qualify_MM(function(resp_mm) {
            console.log("call qualify SM function");
            qualify_SM(function(resp_sm) {
                $.ajax({
                    headers: { "X-CSRFToken": $.cookie("csrftoken") },
                    url: 'http://127.0.0.1:8003/accuracy/analyzeQualitative/',
                    type: 'POST',
                    data: {
                        sketchFileName: resp_mm,
                        metricFileName: resp_sm
                    },
                    success: function(response) {
                        // console.log('Qualitative analysis result:', response);
                        resolve(response); // Resolve the promise with the response data
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        console.error('Error in qualitative analysis:', errorThrown);
                        reject(errorThrown); // Reject the promise with the error message
                    }
                });
            });
        });
    });
}


// function analyzeInputMap(){
// TemporaryAlignmentArray= JSON.parse(JSON.stringify({}));
// TemporaryAlignmentArray = JSON.parse(JSON.stringify(AlignmentArray));
//     qualify_MM(function (resp_mm) {
//         console.log("call qualify SM function");
//         qualify_SM(function(resp_sm){
//             console.log("call the alignment function");
//             // Make an Ajax request for completeness analysis
//             var completenessRequest = $.ajax({
//                 headers: { "X-CSRFToken": $.cookie("csrftoken") },
//                 url: 'http://127.0.0.1:8002/completeness/analyzeCompleteness/',
//                 type: 'POST',
//                 data: {
//                     // qa: $("#qa1").is(':checked'),
//                     sketchFileName: resp_mm,
//                     metricFileName: resp_sm
//                 }
//             });

//             // Make a separate Ajax request for qualitative analysis
//             var qualitativeRequest = $.ajax({
//                 headers: { "X-CSRFToken": $.cookie("csrftoken") },
//                 url: 'http://127.0.0.1:8003/accuracy/analyzeQualitative/',
//                 type: 'POST',
//                 data: {
//                     // qa: $("#qa").is(':checked'),
//                     sketchFileName: "sketchmap",
//                     metricFileName: "basemap"
//                 }
//             });

//             // Combine the results when both requests are complete
//             $.when(completenessRequest, qualitativeRequest).done(function(completenessData, qualitativeData) {
//                 // Handle the combined data here
//                 console.log('Combined completeness data:', completenessData);
//                 console.log('Combined qualitative data:', qualitativeData);

//                 setResults_in_output_div(completenessData, qualitativeData);
//                 $('#summary_result_div').prop("style", " height:100%; overflow-y: scroll;  visibility: visible; position:absolute ; z-index:10000000; background-color: white");
//                 $("#stepper_analyze_map").prop("style", "background: #17a2b8");
//             });

//         });
//     });

//     $(document).on('keydown', function (e) {
//         if (e.keyCode === 27) { // ESC
//             $("#summary_result_div").hide();
//         }
//     });
// }

// function setResults_in_output_div(completenessData,qualitativeData){
//     var amalgamation = 0;
//     var collapse = 0 ;
//     var omissionmerge = 0;
   
   
//      for (var i in Object.values(AlignmentArray)[0]){
//      if (Object.values(AlignmentArray)[0][i].genType == "Amalgamation"){
//       amalgamation = amalgamation + 1 ;
//      }
//      if (Object.values(AlignmentArray)[0][i].genType == "OmissionMerge"){
//       omissionmerge = omissionmerge + 1 ;
//      }
//      if (Object.values(AlignmentArray)[0][i].genType == "Collapse"){
//       collapse = collapse + 1 ;
//      }
//      }
   
   
//        $('#CountOmissionMerge').text(omissionmerge);
//        $('#CountAbsExistenceStreets').text(parseInt(StreetGroup.size) - parseInt(multiOmiMergeCount));
//        $('#CountJunctionMerge').text(junctionmergecount);
//        $('#CountRACollapse').text(roundaboutcount);
//        $('#CountAmalgamation').text(amalgamation);
//        $('#CountAbsExistenceBuildings').text( BuildingGroup.size);
//        $('#CountCollapse').text(collapse);
//        $('#CountOmissionMergeMulti').text(multiOmiMergeCount);
   
   
   
   
//        $('#overAllCompleteness').text(completenessData[0].overAllCompleteness+"%");
//        $('#totalGeneralization').text(parseInt(omissionmerge)+ parseInt(StreetGroup.size)+ parseInt(collapse) + parseInt(junctionmergecount)+ parseInt(roundaboutcount) + parseInt(amalgamation) + parseInt(BuildingGroup.size));
//        $('#precision').text(qualitativeData[0].precision);
//        $('#recall').text(qualitativeData[0].recall);
//        $('#f_score').text(qualitativeData[0].f_score);
//        $('#sketchMapID').text(completenessData[0].sketchMapID);
   
//        $('#total_mm_streets').text(completenessData[0].total_mm_streets);
//        $('#totalSketchedStreets').text(completenessData[0].totalSketchedStreets);
//        $('#streetCompleteness').text(completenessData[0].streetCompleteness  );
   
//        $('#total_mm_landmarks').text(completenessData[0].total_mm_landmarks);
//        $('#totalSketchedLandmarks').text(completenessData[0].totalSketchedLandmarks);
//        $('#landmarkCompleteness').text(completenessData[0].landmarkCompleteness );
   
//        $('#total_mm_cityblocks').text(missingFeaturesCount);
//        $('#totalSketchedCityblocks').text( extraFeaturesCount );
//        $('#cityblockCompleteness').text(completenessData[0].cityblockCompleteness);
//        $('#overAllCompleteness1').text(completenessData[0].overAllCompleteness);
   
//        $('#totalRCC11Relations_mm').text(qualitativeData[0].totalRCC11Relations_mm);
//        $('#totalRCC11Relations').text(qualitativeData[0].totalRCC11Relations);
//        $('#correctRCC11Relations').text(qualitativeData[0].correctRCC11Relations);
//        $('#wrongMatchedRCC11rels').text(qualitativeData[0].wrongMatchedRCC11rels);
//        $('#missingRCC11rels').text(qualitativeData[0].missingRCC11rels);
//        $('#correctnessAccuracy_rcc11').text(qualitativeData[0].correctnessAccuracy_rcc11);
   
//        $('#total_lO_rels_mm').text(qualitativeData[0].total_lO_rels_mm);
//        $('#total_LO_rels_sm').text(qualitativeData[0].total_LO_rels_sm);
//        $('#matched_LO_rels').text(qualitativeData[0].matched_LO_rels);
//        $('#wrong_matched_LO_rels').text(qualitativeData[0].wrong_matched_LO_rels);
//        $('#missing_LO_rels').text(qualitativeData[0].missing_LO_rels);
//        $('#correctnessAccuracy_LO').text(qualitativeData[0].correctnessAccuracy_LO);
   
//        $('#total_LR_rels_mm').text(qualitativeData[0].total_LR_rels_mm);
//        $('#total_LR_rels_sm').text(qualitativeData[0].total_LR_rels_sm);
//        $('#matched_LR_rels').text(qualitativeData[0].matched_LR_rels);
//        $('#wrong_matched_LR_rels').text(qualitativeData[0].wrong_matched_LR_rels);
//        $('#missing_LR_rels').text(qualitativeData[0].missing_LR_rels);
//        $('#correctnessAccuracy_LR').text(qualitativeData[0].correctnessAccuracy_LR);
   
//        $('#total_DE9IM_rels_mm').text(qualitativeData[0].total_DE9IM_rels_mm);
//        $('#total_DE9IM_rels_sm').text(qualitativeData[0].total_DE9IM_rels_sm);
//        $('#matched_DE9IM_rels').text(qualitativeData[0].matched_DE9IM_rels);
//        $('#wrong_matched_DE9IM_rels').text(qualitativeData[0].wrong_matched_DE9IM_rels);
//        $('#missing_DE9IM_rels').text(qualitativeData[0].missing_DE9IM_rels);
//        $('#correctnessAccuracy_DE9IM').text(qualitativeData[0].correctnessAccuracy_DE9IM);
   
//        $('#total_streetTop_rels_mm').text(qualitativeData[0].total_streetTop_rels_mm);
//        $('#total_streetTop_rels_sm').text(qualitativeData[0].total_streetTop_rels_sm);
//        $('#matched_streetTop_rels').text(qualitativeData[0].matched_streetTop_rels);
//        $('#wrong_matched_streetTop_rels').text(qualitativeData[0].wrong_matched_streetTop_rels);
//        $('#missing_streetTop_rels').text(qualitativeData[0].missing_streetTop_rels);
//        $('#correctnessAccuracy_streetTop').text(qualitativeData[0].correctnessAccuracy_streetTop);
   
//        $('#total_opra_rels_mm').text(qualitativeData[0].total_opra_rels_mm);
//        $('#total_opra_rels_sm').text(qualitativeData[0].total_opra_rels_sm);
//        $('#matched_opra_rels').text(qualitativeData[0].matched_opra_rels);
//        $('#wrong_matched_opra_rels').text(qualitativeData[0].wrong_matched_opra_rels);
//        $('#missing_opra_rels').text(qualitativeData[0].missing_opra_rels);
//        $('#correctnessAccuracy_opra').text(qualitativeData[0].correctnessAccuracy_opra);
   
//    }
   
// Function to handle completeness results
function handleCompletenessResults(completenessData) {
    var completeness = completenessData;
    // Update DOM elements
    $('#overAllCompleteness').text(completeness.overAllCompleteness + "%");
    $('#sketchMapID').text(completeness.sketchMapID);
    $('#total_mm_streets').text(completeness.total_mm_streets);
    $('#totalSketchedStreets').text(completeness.totalSketchedStreets);
    $('#streetCompleteness').text(completeness.streetCompleteness);
    $('#total_mm_landmarks').text(completeness.total_mm_landmarks);
    $('#totalSketchedLandmarks').text(completeness.totalSketchedLandmarks);
    $('#landmarkCompleteness').text(completeness.landmarkCompleteness);
    $('#total_mm_cityblocks').text(missingFeaturesCount);
    $('#totalSketchedCityblocks').text(extraFeaturesCount);
    $('#cityblockCompleteness').text(completeness.cityblockCompleteness);
    $('#overAllCompleteness1').text(completeness.overAllCompleteness);

}

function handleCorrectnessResults(qualitativeData) {
    var qualitative = qualitativeData;
    if (qualitative) {
        $('#precision').text(qualitative.precision);
        $('#recall').text(qualitative.recall);
        $('#f_score').text(qualitative.f_score);
        $('#totalRCC11Relations_mm').text(qualitative.totalRCC11Relations_mm);
        $('#totalRCC11Relations').text(qualitative.totalRCC11Relations);
        $('#correctRCC11Relations').text(qualitative.correctRCC11Relations);
        $('#wrongMatchedRCC11rels').text(qualitative.wrongMatchedRCC11rels);
        $('#missingRCC11rels').text(qualitative.missingRCC11rels);
        $('#correctnessAccuracy_rcc11').text(qualitative.correctnessAccuracy_rcc11);

        $('#total_lO_rels_mm').text(qualitative.total_lO_rels_mm);
        $('#total_LO_rels_sm').text(qualitative.total_LO_rels_sm);
        $('#matched_LO_rels').text(qualitative.matched_LO_rels);
        $('#wrong_matched_LO_rels').text(qualitative.wrong_matched_LO_rels);
        $('#missing_LO_rels').text(qualitative.missing_LO_rels);
        $('#correctnessAccuracy_LO').text(qualitative.correctnessAccuracy_LO);

        $('#total_LR_rels_mm').text(qualitative.total_LR_rels_mm);
        $('#total_LR_rels_sm').text(qualitative.total_LR_rels_sm);
        $('#matched_LR_rels').text(qualitative.matched_LR_rels);
        $('#wrong_matched_LR_rels').text(qualitative.wrong_matched_LR_rels);
        $('#missing_LR_rels').text(qualitative.missing_LR_rels);
        $('#correctnessAccuracy_LR').text(qualitative.correctnessAccuracy_LR);

        $('#total_DE9IM_rels_mm').text(qualitative.total_DE9IM_rels_mm);
        $('#total_DE9IM_rels_sm').text(qualitative.total_DE9IM_rels_sm);
        $('#matched_DE9IM_rels').text(qualitative.matched_DE9IM_rels);
        $('#wrong_matched_DE9IM_rels').text(qualitative.wrong_matched_DE9IM_rels);
        $('#missing_DE9IM_rels').text(qualitative.missing_DE9IM_rels);
        $('#correctnessAccuracy_DE9IM').text(qualitative.correctnessAccuracy_DE9IM);

        $('#total_streetTop_rels_mm').text(qualitative.total_streetTop_rels_mm);
        $('#total_streetTop_rels_sm').text(qualitative.total_streetTop_rels_sm);
        $('#matched_streetTop_rels').text(qualitative.matched_streetTop_rels);
        $('#wrong_matched_streetTop_rels').text(qualitative.wrong_matched_streetTop_rels);
        $('#missing_streetTop_rels').text(qualitative.missing_streetTop_rels);
        $('#correctnessAccuracy_streetTop').text(qualitative.correctnessAccuracy_streetTop);

        $('#total_opra_rels_mm').text(qualitative.total_opra_rels_mm);
        $('#total_opra_rels_sm').text(qualitative.total_opra_rels_sm);
        $('#matched_opra_rels').text(qualitative.matched_opra_rels);
        $('#wrong_matched_opra_rels').text(qualitative.wrong_matched_opra_rels);
        $('#missing_opra_rels').text(qualitative.missing_opra_rels);
        $('#correctnessAccuracy_opra').text(qualitative.correctnessAccuracy_opra);
    }
}

function handlegeneralizationResults(){
 var amalgamation = 0;
 var collapse = 0 ;
 var omissionmerge = 0;

  for (var i in Object.values(AlignmentArray)[0]){
  if (Object.values(AlignmentArray)[0][i].genType == "Amalgamation"){
   amalgamation = amalgamation + 1 ;
  }
  if (Object.values(AlignmentArray)[0][i].genType == "OmissionMerge"){
   omissionmerge = omissionmerge + 1 ;
  }
  if (Object.values(AlignmentArray)[0][i].genType == "Collapse"){
   collapse = collapse + 1 ;
  }
  }

    $('#CountOmissionMerge').text(omissionmerge);
    $('#CountAbsExistenceStreets').text(parseInt(StreetGroup.size) - parseInt(multiOmiMergeCount));
    $('#CountJunctionMerge').text(junctionmergecount);
    $('#CountRACollapse').text(roundaboutcount);
    $('#CountAmalgamation').text(amalgamation);
    $('#CountAbsExistenceBuildings').text( BuildingGroup.size);
    $('#CountCollapse').text(collapse);
    $('#CountOmissionMergeMulti').text(multiOmiMergeCount);
    $('#totalGeneralization').text(parseInt(omissionmerge)+ parseInt(StreetGroup.size)+ parseInt(collapse) + parseInt(junctionmergecount)+ parseInt(roundaboutcount) + parseInt(amalgamation) + parseInt(BuildingGroup.size));

}


function findCommonElements3(arr1, arr2) {
    return arr1.some(item => arr2.includes(item))
}


$( "#exportAsCSV" ).on( "click", function() {
var GeneralizationCSV = ["BaseId , SketchId , Generalization Type"];
var QualRelationsBaseMapCSV = ["Object 1 , Object 2, Relations"];
var QualRelationsSketchMapCSV = ["Object 1, Object 2, Relations"];

        for (var x in qualRelationsBaseMap.constraint_collection){

            QualRelationsBaseMapCSV.push(" " + ',' +  qualRelationsBaseMap.constraint_collection[x].relation_set + ',' + " ");
            for (var y in  qualRelationsBaseMap.constraint_collection[x].constraints){
            QualRelationsBaseMapCSV.push(qualRelationsBaseMap.constraint_collection[x].constraints[y]["obj 1"] + ',' + qualRelationsBaseMap.constraint_collection[x].constraints[y]["obj 2"] + ',' + qualRelationsBaseMap.constraint_collection[x].constraints[y]["relation"])
            }
        }

        for (var x in qualRelationsSketchMap.constraint_collection){
            QualRelationsSketchMapCSV.push(" " + ',' +  qualRelationsSketchMap.constraint_collection[x].relation_set + ',' + " ");
            for (var y in  qualRelationsSketchMap.constraint_collection[x].constraints){
            QualRelationsSketchMapCSV.push(qualRelationsSketchMap.constraint_collection[x].constraints[y]["obj 1"] + ',' + qualRelationsSketchMap.constraint_collection[x].constraints[y]["obj 2"] + ',' + qualRelationsSketchMap.constraint_collection[x].constraints[y]["relation"])
            }
        }

    Object.keys(TemporaryAlignmentArray[sketchMaptitle]).forEach(function(key){
     if (key != "checkAlignnum"){
       if (findCommonElements3(multiOmiMergeids, TemporaryAlignmentArray[sketchMaptitle][key].BaseAlign[0])){
            TemporaryAlignmentArray[sketchMaptitle][key].genType = "Multi-Multi Omission Merge";
          }
     }

    });



    Object.keys(TemporaryAlignmentArray[sketchMaptitle]).forEach(function(key) {

        if (key != "checkAlignnum"){
        if (findCommonElements3(junctionmergeids, TemporaryAlignmentArray[sketchMaptitle][key].BaseAlign[0])){
             if (TemporaryAlignmentArray[sketchMaptitle][key].genType == "No generalization") {
                    TemporaryAlignmentArray[sketchMaptitle][key].genType = "JunctionMerge" ;
                    }
             else {
                      console.log("check check" ,TemporaryAlignmentArray[sketchMaptitle][key])
                      TemporaryAlignmentArray[sketchMaptitle][key].genType = TemporaryAlignmentArray[sketchMaptitle][key].genType + "JunctionMerge" ;
             }
          }
           if (findCommonElements3(roundaboutids, TemporaryAlignmentArray[sketchMaptitle][key].BaseAlign[0])){
            console.log("YEsCSV");
                if (TemporaryAlignmentArray[sketchMaptitle][key].genType == "No generalization") {
                    TemporaryAlignmentArray[sketchMaptitle][key].genType = "RoundAboutCollapse"
                    }
                else {
                    TemporaryAlignmentArray[sketchMaptitle][key].genType = TemporaryAlignmentArray[sketchMaptitle][key].genType + "RoundAboutCollapse"
                }
          }
        GeneralizationCSV.push(((TemporaryAlignmentArray[sketchMaptitle][key].BaseAlign[0]).toString()).replaceAll(",", " ") + ',' + ((TemporaryAlignmentArray[sketchMaptitle][key].SketchAlign[0]).toString()).replaceAll(",", " ") + ',' + ((TemporaryAlignmentArray[sketchMaptitle][key].genType).toString()) ) ;

        }
   // do something with key or value

    });

        GeneralizationCSV.push("Features missing in sketch map, " + missingFeaturesIds.toString());
        GeneralizationCSV.push("Features drawn extra in sketch map, " + extraFeaturesIds.toString());

    var html = document.querySelector("#correctness >table").outerHTML;


   var csv = [];
    var rows = document.querySelectorAll("table tr");
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        for (var j = 0; j < cols.length; j++)
            row.push(cols[j].innerText);
        csv.push(row.join(","));
    }






    var zip = new JSZip();
        zip.file("GenDetailedOutput.csv",GeneralizationCSV.join("\n"));
        zip.file("QRBaseMap.csv",QualRelationsBaseMapCSV.join("\n"));
        zip.file("QRSketchMap.csv",QualRelationsSketchMapCSV.join("\n"));
        zip.file(sketchMaptitle + "QualitativeOutput.csv", csv.join("\n"));
        zip.file("GeneralizedBaseMap.geojson", JSON.stringify(GenBaseMap.toGeoJSON()));
        zip.generateAsync({type:"blob"})
        .then(function(content) {
        saveAs(content, sketchMaptitle.replace(".jpg","") + "Output.zip");
      });

});


