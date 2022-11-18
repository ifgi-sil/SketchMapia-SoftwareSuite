var GenBaseMap;
var ProcSketchMap;






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
                    console.log(e.target);
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
    saveAs(content, "project.zip");

});
}

function qualify_MM(callback) {
    MMGeoJsonData = GenBaseMap.toGeoJSON();
    console.log("metric map jsondata:",MMGeoJsonData);

    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'mmReceiver/',
        type: 'POST',
        data:
            {
                metricFileName: "basemap",
                MMGeoJsonData: JSON.stringify(MMGeoJsonData)
            },
        //contentType: 'application/json',
        success: function (resp) {
            console.log("Metric Map Qualify complete");
            callback();
        }
    });
}

function qualify_SM(callback) {
    SMGeoJsonData = ProcSketchMap.toGeoJSON();
    console.log("SMGeoJsonData....:",SMGeoJsonData);
    // fileName = sketchFileName.split(".");
    // fileName = fName[0];

    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'smReceiver/',
        type: 'POST',
        data: {
            sketchFileName:"sketchmap",
            SMGeoJsonData: JSON.stringify(SMGeoJsonData)
        },
        //dataType: 'json',
        success: function (resp) {
            console.log("Sketch Map Qualify complete");
            callback();
        }
    });
}



function generalizeMap(){
        console.log ("checkalign", checkAlignnum);
         drawnItems.eachLayer(function(blayer){
        if (!blayer.feature.properties.aligned ){
            blayer.feature.properties.missing = true;
        }
        else
        {delete blayer.feature.properties.missing; }
        });
        drawnSketchItems.setStyle({opacity:1});
        AlignmentArray[sketchMaptitle]=alignmentArraySingleMap;
        AlignmentArray[sketchMaptitle].checkAlignnum = checkAlignnum;


console.log(AlignmentArray);
var lastBaseStreet = routeArray[routeArray.length - 1];

if (routeArray.length == 0){
  drawnItems.eachLayer(function(blayer){
           if (blayer.feature.properties.isRoute == "Yes"){
              routeArray.push(blayer.feature.properties.id);
  }
 });
}
lastBaseStreet = routeArray[routeArray.length - 1];
var lastSketchStreet = sketchRouteArray[sketchRouteArray.length -1];


var url = "http://localhost:80/fmedatastreaming/sketchMapia/generalizerFile.fmw?Alignment=" + encodeURIComponent(JSON.stringify(JSON.stringify(AlignmentArray))) + "&RouteSeq=" + encodeURIComponent(routeArray) + "&SketchRouteSeq=" + encodeURIComponent(sketchRouteArray) + "&lastsegment=" + encodeURIComponent(lastBaseStreet) + "&lastsketchsegment=" + encodeURIComponent(lastSketchStreet);
var newurl = "http://desktop-f25rpfv:8080/fmerest/v3/repositories/GeneralizationPredict/networkcalculator.fmw/parameters?fmetoken=47e241ca547e14ab6ea961aef083f8a4cbe6dfe3"

 $.ajax({
                headers: { "X-CSRFToken": $.cookie("csrftoken") },
                url: 'requestFME/',
                type: 'POST',
                data: {
                    basedata: JSON.stringify(drawnItems.toGeoJSON()),
                    sketchdata: JSON.stringify(drawnSketchItems.toGeoJSON())
                },
                //contentType: 'text/plain',
                success: function (resp) {
                   console.log("Test done");
                   var httpRequest = new XMLHttpRequest();
                    httpRequest.open("GET", url, false);
                    httpRequest.setRequestHeader("Authorization","fmetoken token=f334fd1f73b3782bd463598970a4709df01b4a09")
                    httpRequest.setRequestHeader("Access-Control-Allow-Origin", "http://localhost:80");
                    httpRequest.setRequestHeader("Accept","text/html");
                    httpRequest.setRequestHeader("content-Type","multipart/form-data");
            httpRequest.onreadystatechange = function()
            {
                if (httpRequest.readyState == 4 && httpRequest.status == 200)
                {

                var randomnum = 110111;
                var wholeMapProc = JSON.parse(httpRequest.response);
                var sketchMapProc=[];
                var baseMapProc=[];
                 $.each(wholeMapProc.features, function(i, item) {
                 if(item.properties.mapType == "Sketch"){
                    if(item.properties.otype == "CircleMarker"){
                        item.properties.feat_type="Landmark";
                        }

                    sketchMapProc.push(item);
                 }
                 else{

                  if (item.properties.missing){
                  item.properties.id = randomnum;
                  }
                   if (item.properties.SketchAlign){
                    item.properties.id = Object.values(JSON.parse(item.properties.SketchAlign))[0][0].replace(/\D/g,'');
                 }
                  baseMapProc.push(item);
                  randomnum = randomnum + 1;
                 }
                 });

                if (GenBaseMap != null) {
                    layerGroupBasemapGen.removeLayer(GenBaseMap);
                 }


                GenBaseMap = L.geoJSON(baseMapProc);
                GenBaseMap.eachLayer(function(glayer){


            if (!glayer.feature.properties.selected && glayer.feature.properties.missing == "Yes" && !glayer.feature.properties.isRoute){
                glayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: [5, 5]});
            }
            if (!glayer.feature.properties.selected && !glayer.feature.properties.missing && !glayer.feature.properties.isRoute){
                glayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: null});
            }
            if (!glayer.feature.properties.selected && glayer.feature.properties.missing == "Yes" && glayer.feature.properties.isRoute=="Yes"){
                glayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: [5, 5]});
            }
            if(!glayer.feature.properties.selected && !glayer.feature.properties.missing && glayer.feature.properties.isRoute=="Yes"){
                glayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: null,});
            }
     });
                GenBaseMap.addTo(layerGroupBasemapGen);


                console.log(baseMapProc);
                ProcSketchMap = L.geoJSON(sketchMapProc);
                analyzeInputMap();
                }
            }
            // send a request so we get a reply
            httpRequest.send();

                }
            });

/*

*/

}





function analyzeInputMap(){


    //loc = document.getElementById("#sketchmapplaceholder");
    //createProcessingRing(loc);

    //sm_map.addLayer(createProcessingRing(loc));
    //sm_map.addLayer( createProcessingRing(loc));
    qualify_MM(function () {
        console.log("call qualify SM function");
        qualify_SM(function(){
            console.log("call the alignment function");
            // ajax call for getting the matches dictionary
            $.ajax({
                headers: { "X-CSRFToken": $.cookie("csrftoken") },
                url: 'analyzeInputMap/',
                type: 'POST',
                data: {
                    sketchFileName: "sketchmap",
                    metricFileName: "basemap"

                },
                //contentType: 'text/plain',
                success: function (resp) {
                    console.log(resp);
                    setResults_in_output_div(resp);
                    $('#summary_result_div').prop("style", "visibility: visible; position:absolute ; z-index:10000000; background-color: white");
                    //$('#summary_result_div').refresh();

                    $("#stepper_analyze_map").prop("style", "background: #17a2b8");
                    //window.open('http://127.0.0.1:5000/resultSummary','_blank');
                    //deleteProcessingRing(loc);
                }
            });
        });
    });

    $(document).on('keydown', function (e) {
        if (e.keyCode === 27) { // ESC
            $("#summary_result_div").hide();
        }
    });
}

function setResults_in_output_div(resp){

 console.log(Object.values(AlignmentArray)[0]);
 var amalgamation = "";
 var collapse = "";
 var omissionmerge = "";

  for (var i in Object.values(AlignmentArray)[0]){
  console.log(i)
  if (Object.values(AlignmentArray)[0][i].genType == "Amalgamation"){
   amalgamation = amalgamation + "    " + Object.values(AlignmentArray)[0][i].degreeOfGeneralization ;
  }
  if (Object.values(AlignmentArray)[0][i].genType == "OmissionMerge"){
   omissionmerge = omissionmerge + "    " + Object.values(AlignmentArray)[0][i].degreeOfGeneralization ;
  }
  if (Object.values(AlignmentArray)[0][i].genType == "Collapse"){
   collapse = collapse + "    " + Object.values(AlignmentArray)[0][i].degreeOfGeneralization ;
  }

  }

    $('#Amalgamation').text(amalgamation);
    $('#OmissionMerge').text(omissionmerge);
    $('#Collapse').text(collapse);

    $('#overAllCompleteness').text(resp.overAllCompleteness+"%");
    $('#precision').text(resp.precision);
    $('#recall').text(resp.recall);
    $('#f_score').text(resp.f_score);
    $('#sketchMapID').text(resp.sketchMapID);

    $('#toal_mm_streets').text(resp.toal_mm_streets);
    $('#totalSketchedStreets').text(resp.totalSketchedStreets);
    $('#streetCompleteness').text(resp.streetCompleteness);

    $('#total_mm_landmarks').text(resp.total_mm_landmarks);
    $('#totalSketchedLandmarks').text(resp.totalSketchedLandmarks);
    $('#landmarkCompleteness').text(resp.landmarkCompleteness);

    $('#total_mm_cityblocks').text(resp.total_mm_cityblocks);
    $('#totalSketchedCityblocks').text(resp.totalSketchedCityblocks);
    $('#cityblockCompleteness').text(resp.cityblockCompleteness);
    $('#overAllCompleteness1').text(resp.overAllCompleteness);

    $('#totalRCC11Relations_mm').text(resp.totalRCC11Relations_mm);
    $('#totalRCC11Relations').text(resp.totalRCC11Relations);
    $('#correctRCC11Relations').text(resp.correctRCC11Relations);
    $('#wrongMatchedRCC11rels').text(resp.wrongMatchedRCC11rels);
    $('#missingRCC11rels').text(resp.missingRCC11rels);
    $('#correctnessAccuracy_rcc11').text(resp.correctnessAccuracy_rcc11);

    $('#total_lO_rels_mm').text(resp.total_lO_rels_mm);
    $('#total_LO_rels_sm').text(resp.total_LO_rels_sm);
    $('#matched_LO_rels').text(resp.matched_LO_rels);
    $('#wrong_matched_LO_rels').text(resp.wrong_matched_LO_rels);
    $('#missing_LO_rels').text(resp.missing_LO_rels);
    $('#correctnessAccuracy_LO').text(resp.correctnessAccuracy_LO);

    $('#total_LR_rels_mm').text(resp.total_LR_rels_mm);
    $('#total_LR_rels_sm').text(resp.total_LR_rels_sm);
    $('#matched_LR_rels').text(resp.matched_LR_rels);
    $('#wrong_matched_LR_rels').text(resp.wrong_matched_LR_rels);
    $('#missing_LR_rels').text(resp.missing_LR_rels);
    $('#correctnessAccuracy_LR').text(resp.correctnessAccuracy_LR);

    $('#total_DE9IM_rels_mm').text(resp.total_DE9IM_rels_mm);
    $('#total_DE9IM_rels_sm').text(resp.total_DE9IM_rels_sm);
    $('#matched_DE9IM_rels').text(resp.matched_DE9IM_rels);
    $('#wrong_matched_DE9IM_rels').text(resp.wrong_matched_DE9IM_rels);
    $('#missing_DE9IM_rels').text(resp.missing_DE9IM_rels);
    $('#correctnessAccuracy_DE9IM').text(resp.correctnessAccuracy_DE9IM);

    $('#total_streetTop_rels_mm').text(resp.total_streetTop_rels_mm);
    $('#total_streetTop_rels_sm').text(resp.total_streetTop_rels_sm);
    $('#matched_streetTop_rels').text(resp.matched_streetTop_rels);
    $('#wrong_matched_streetTop_rels').text(resp.wrong_matched_streetTop_rels);
    $('#missing_streetTop_rels').text(resp.missing_streetTop_rels);
    $('#correctnessAccuracy_streetTop').text(resp.correctnessAccuracy_streetTop);

    $('#total_opra_rels_mm').text(resp.total_opra_rels_mm);
    $('#total_opra_rels_sm').text(resp.total_opra_rels_sm);
    $('#matched_opra_rels').text(resp.matched_opra_rels);
    $('#wrong_matched_opra_rels').text(resp.wrong_matched_opra_rels);
    $('#missing_opra_rels').text(resp.missing_opra_rels);
    $('#correctnessAccuracy_opra').text(resp.correctnessAccuracy_opra);



}