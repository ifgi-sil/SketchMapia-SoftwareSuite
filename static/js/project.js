var GenBaseMap;
var ProcSketchMap;

function uploadProject(){
    console.log("upload");
}


function downloadProject(){
 var alignment = JSON.stringify(AlignmentArray);
 var zip = new JSZip();
 zip.file("alignment.json",alignment);
 for (var key in allDrawnSketchItems) {
    zip.file(key + ".geojson", JSON.stringify(allDrawnSketchItems[key].toGeoJSON()) );
    console.log(key + ' is ' + allDrawnSketchItems[key]);
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



function generalizeMap(baseMap,sketchMap){
console.log(routeArray);
console.log(sketchRouteArray);
var lastBaseStreet = routeArray[routeArray.length - 1];
var lastSketchStreet = sketchRouteArray[sketchRouteArray.length -1];
var url = "http://desktop-f25rpfv:8080/fmedatastreaming/Generalization/generalizer.fmw?baseMap=" + encodeURIComponent(JSON.stringify(JSON.stringify(baseMap.toGeoJSON()))) + "&sketchMap=" + encodeURIComponent(JSON.stringify(JSON.stringify(sketchMap.toGeoJSON()))) + "&Alignment=" + encodeURIComponent(JSON.stringify(JSON.stringify(AlignmentArray))) + "&RouteSeq=" + encodeURIComponent(routeArray) + "&SketchRouteSeq=" + encodeURIComponent(sketchRouteArray) + "&lastsegment=" + encodeURIComponent(lastBaseStreet) + "&lastsketchsegment=" + encodeURIComponent(lastSketchStreet);
var newurl = "http://desktop-f25rpfv:8080/fmerest/v3/repositories/GeneralizationPredict/networkcalculator.fmw/parameters?fmetoken=47e241ca547e14ab6ea961aef083f8a4cbe6dfe3"


var httpRequest = new XMLHttpRequest();
httpRequest.open("GET", url, false);
httpRequest.setRequestHeader("Authorization","fmetoken token=c1f02207ac3b1489be2c18ee26cefb643d646bce")
httpRequest.setRequestHeader("Access-Control-Allow-Origin", "http://desktop-f25rpfv:8080");
httpRequest.setRequestHeader("Accept","text/html");
httpRequest.setRequestHeader("content-Type","application/x-www-form-urlencoded");
            httpRequest.onreadystatechange = function()
            {
                if (httpRequest.readyState == 4 && httpRequest.status == 200)
                {


                var wholeMapProc = JSON.parse(httpRequest.response);
                var sketchMapProc=[];
                var baseMapProc=[];
                 $.each(wholeMapProc.features, function(i, item) {
                 if(item.properties.mapType == "Sketch"){
                    sketchMapProc.push(item);
                 }
                 else{
                    item.properties.id = Object.values(JSON.parse(item.properties.SketchAlign))[0][0].replace(/\D/g,'');
                    baseMapProc.push(item);
                 }
                 });

                console.log(sketchMapProc);
                console.log(baseMapProc);

                GenBaseMap = L.geoJSON(baseMapProc);

                layerGroupBasemap.addLayer(GenBaseMap);
                ProcSketchMap = L.geoJSON(sketchMapProc);
                }
            }
            // send a request so we get a reply
            httpRequest.send();



}


function onAnalyseButtonClick(){
$.ajax({
    url:   generalizeMap(drawnItems,drawnSketchItems),
    success: function(){
    analyzeInputMap();
    }
})


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