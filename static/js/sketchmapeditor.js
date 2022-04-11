

var sketchMap;
var sketchMaptitle;
var drawnSketchItems;
var alignSketchID=[];
var sketchOtypearray={};
var baseOtypearray={};
var alignBaseID=[];
var allDrawnSketchItems={};
var AlignmentArray = {};
var checkAlignnum;
var alignmentArraySingleMap={};
var id=0;
var bid=-1;




$(function() {

    $('.btn-link[aria-expanded="true"]').closest('.accordion-item').addClass('active');
  $('.collapse').on('show.bs.collapse', function () {
	  $(this).closest('.accordion-item').addClass('active');
	});

  $('.collapse').on('hidden.bs.collapse', function () {
	  $(this).closest('.accordion-item').removeClass('active');
	});



});


$( "#filemenu" ).click(function() {
  $( "#filemenuoptions" ).slideToggle(500);
});

$( "#editmenu" ).click(function() {
  $( "#editmenuoptions" ).slideToggle(500);
});




function loadFromImage(){
var imageList = document.getElementById('fromfile').files;
$("#loadbasemap").hide();
$("#imagemap").show();
    for (var i = 0; i < imageList.length; i++) {
        renderImageFile(imageList[i], location);
    }
}

var baseMap;
var drawnItems;

function renderImageFile(file, location) {
    var reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = function (e) {

        var container = L.DomUtil.get('baseMap');
        if (container != null) {
            container._leaflet_id = null;
        }
        var image = new Image();

        image.title = file.name;
        image.src = this.result;


        baseMap = new L.map('imagemap', {
            crs: L.CRS.Simple
        });

 var bounds = [[0, 0], [600, 850]];

        var BMLoaded = new L.imageOverlay(image.src,bounds);
        BMLoaded.addTo(baseMap);
        baseMap.fitBounds(bounds);
        drawnItems = new L.geoJson().addTo(baseMap);
    }

$( "#loaded" ).prop( "checked", true );
$( "#loaded" ).prop( "disabled", false );



}



var drawBM = document.getElementById('drawBM');
$('#drawBM').click(function(){

baseMap.pm.addControls({
position: 'topleft',
drawCircle: false,
drawMarker: false,
drawRectangle:false,
drawCircleMarker:true,
dragMode:false,
rotateMode:false,
cutPolygon:false
});

baseMap.on('pm:create', function (event) {
    bid=bid+1;
    var layer = event.layer;
    layer.otype = event.shape;
    layer.id=bid;
    var feature = layer.feature = layer.feature || {}; // Initialize feature
    feature.type = feature.type || "Feature"; // Initialize feature.type
    var props = feature.properties = feature.properties || {}; // Initialize feature.properties
    props.id = bid;
    props.isRoute = "Yes";
    if(event.shape == "Polygon"){
    props.feat_type = "Landmark"
    }
    else{
    props.feat_type = null;}
    layer.selected=false;
    layer.aligned=false;
    drawnItems.addLayer(layer);
    console.log(event.layer._latlng);
});


baseMap.pm.setGlobalOptions({
  pathOptions:{
    opacity:0.7,
    weight: 5,
    color: "#e8913a",
    radius: 5},
  templineStyle: {
    color: "#e8913a",
  },
  hintlineStyle: {
    color: "#e8913a",
    dashArray: [5, 5],
  }

});
$( "#editmenuoptions" ).slideToggle(500);

drawnItems.eachLayer(function(blayer){
        blayer.off('click');
        });

});




$("#saveBM").click(function(){
$( "#marked" ).prop( "checked", true );
$( "#marked" ).prop( "disabled", false );
baseMap.pm.removeControls();
drawnItems.setStyle({opacity:1});
addClickBase();
$( "#editmenuoptions" ).slideToggle(500);
});

function addClickBase(){
drawnItems.eachLayer(function(blayer){
        blayer.on('click',function(e){
        if(blayer.selected==false){
            blayer.selected=true;
            alignBaseID.push(blayer.id);
            console.log("selected", blayer.id);
            baseOtypearray[blayer.id]=blayer.otype;
            styleLayers();
        }
        else{
            blayer.selected = false;
            alignBaseID= alignBaseID.filter(function(item) {
                return item !== blayer.id;
            })
            delete baseOtypearray[blayer.id];
            console.log("deselected", blayer.id);
            styleLayers();
        }
    });
    });
}


   $('.thumbnail').click(function(e){


        if (sketchMap != null) {
            sketchMap.remove();
            addClickBase();
            console.log("**thum");
        }
        var image = new Image();
        image.src = $(e.target).attr('src');

        sketchMap = new L.map('sketchimagemap', {
            crs: L.CRS.Simple
        });
        sketchMap.getContainer().focus = ()=>{};

        var bounds = [[0, 0], [600, 850]];
        var SMLoaded = new L.imageOverlay(image.src,bounds);
        SMLoaded.addTo(sketchMap);
        sketchMap.fitBounds(bounds);
        sketchMaptitle = $(e.target).parent().attr("data-original-title");
        console.log("*");
        if(allDrawnSketchItems.hasOwnProperty(sketchMaptitle)){
        drawnSketchItems=allDrawnSketchItems[sketchMaptitle];
        drawnSketchItems.addTo(sketchMap);
        alignmentArraySingleMap=AlignmentArray[sketchMaptitle];
        id=AlignmentArray[sketchMaptitle].id+1;
        checkAlignnum = AlignmentArray[sketchMaptitle].checkAlignnum+1;
        restoreBaseAlignment(alignmentArraySingleMap);
        styleLayers();
        console.log("***");
        }
        else{
        drawnSketchItems = new L.geoJson().addTo(sketchMap);
        alignmentArraySingleMap={};
        drawnItems.eachLayer(function(blayer){
            blayer.selected=false;
            blayer.aligned=false;

        });
        styleLayers();
        id = 0;
        checkAlignnum = 1;
        console.log("*****");
        }
   });



    $('#drawSM').click(function(){
        sketchMap.pm.addControls({
            position: 'topleft',
            drawCircle: false,
            drawRectangle:false,
            drawMarker:false,
            drawCircleMarker:true,
            dragMode:false,
            rotateMode:false,
            cutPolygon:false
    });
    sketchMap.pm.setGlobalOptions({
            pathOptions:{
                opacity:0.7,
                weight: 5,
                color: "#e8913a",
                radius: 5
                },
            templineStyle: {
                color: "#e8913a",
             },
            hintlineStyle: {
                color: "#e8913a",
                dashArray: [5, 5],
            }
        });


        sketchMap.on('pm:create', function (event) {
            var layer = event.layer;
            layer.id='S'+id;
            var feature = layer.feature = layer.feature || {}; // Initialize feature
            feature.type = feature.type || "Feature"; // Initialize feature.type
            var props = feature.properties = feature.properties || {}; // Initialize feature.properties
            props.id = id;
            props.isRoute = "Yes";
            console.log(event.shape);
             if(event.shape == "Polygon"){
    props.feat_type = "Landmark"
    }
    else{
    props.feat_type = null;}
            layer.selected = false;
            layer.aligned = false;
            layer.otype = event.shape;
            drawnSketchItems.addLayer(layer);
            id=id+1;

        layer.on('click', function (e) {
        if(layer.selected==false){
            layer.selected = true;
            alignSketchID.push(layer.id);
            sketchOtypearray[layer.id]=layer.otype;
            console.log("selected sketch", layer.id);
            styleLayers();
            }
        else{
            layer.selected = false;
            alignSketchID= alignSketchID.filter(function(item) {
                return item !== layer.id;
            });
            console.log("deselected sketch", layer.id);
            delete sketchOtypearray[layer.id];
            styleLayers();
        }
        });

     });


    $( "#editmenuoptions" ).slideToggle(500);
    });



    $('#alignbutton').click(function(){
        checkIfAlignedAlready(alignSketchID);
        drawnSketchItems.eachLayer(function(slayer){
        if (alignSketchID.includes(slayer.id)){
        slayer.aligned = true;
        slayer.selected = false;
        styleLayers();
        }
        });
        drawnItems.eachLayer(function(blayer){
        if (alignBaseID.includes(blayer.id)){
        blayer.aligned = true;
        blayer.selected = false;
        styleLayers();
        }
        });
        align(alignBaseID,alignSketchID,checkAlignnum,sketchOtypearray,baseOtypearray);
        checkAlignnum=checkAlignnum+1;
    });




    function align(BID,SID,num,sketchtype,basetype){
       var BaseAlign={};
       var SketchAlign={};
            BaseAlign[num]=BID;
            SketchAlign[num]=SID;
       var genType;
       (async () => {
          genType = await predictGeneralization(sketchtype,basetype);
          alignmentArraySingleMap[num]={BaseAlign,SketchAlign,genType};
          console.log("aligned", alignmentArraySingleMap);
        })()

       alignBaseID=[];
       alignSketchID=[];
       sketchOtypearray = {};
       baseOtypearray = {};
       hoverfunction();
    }
    var hoverarray = [];
    function hoverfunction(){

    drawnSketchItems.eachLayer(function(slayer){
    slayer.on('mouseover', function() {
    $.each(alignmentArraySingleMap, function(i, item) {
    if((alignmentArraySingleMap[i].SketchAlign != null) && Object.values(alignmentArraySingleMap[i].SketchAlign).includes(slayer.id)){
    hoverarray.push(Object.values(alignmentArraySingleMap[i].BaseAlign));
    hoverarray.push(Object.values(alignmentArraySingleMap[i].SketchAlign));
    }
    changestyleOnHover(hoverarray);
    });
    });
    slayer.on('mouseout', function() {
    hoverarray=[];
    styleLayers();
    });

    });
    }


  function predictGeneralization(sketchtype,basetype){
        if (checktype(sketchtype,basetype)){
            switch (sketchtype[Object.keys(sketchtype)[0]]){
                case "Line":
                    switch (checkgroupalign(sketchtype,basetype)){
                        case "one-one":
                            return "No generalization";
                            break;
                        case "one-many":
                            return predictGenSingleLine(sketchtype,basetype);
                            break;
                        case "many-many":
                            return predictGenMultiLine(sketchtype,basetype);
                            break;
                    }
                    break;
                case "Polygon":
                    switch (checkgroupalign(sketchtype,basetype)){
                        case "one-one":
                            return "No generalisation";
                            break;
                        case "one-many":
                            return "Amalgamation";
                            break;
                        case "many-many":
                            return "Abstraction to show existence";
                            break;
                    }
                    break;
            }

        }
        else if(sketchtype[Object.keys(sketchtype)[0]]=="CircleMarker" || basetype[Object.keys(basetype)[0]]=="CircleMarker"){
            return "Collapse";
        }
        else{
        alert("Error Cannot Align :Basemap feature type is different from sketchmap feature type");
        }
    }

    function checktype(sketchtype,basetype){
     const allOtype = {...sketchtype,...basetype}
     return new Set(Object.values(allOtype)).size === 1;
    }

    function checkgroupalign(sketchtype,basetype){
        if (Object.keys(sketchtype).length == 1 && Object.keys(basetype).length==1){
            return "one-one";
        }
        if (Object.keys(sketchtype).length == 1 && Object.keys(basetype).length > 1){
            return "one-many";
        }
        if(Object.keys(sketchtype).length > 1 && Object.keys(basetype).length>1){
            return "many-many";
        }
    }


    function changestyleOnHover(Array){
    Array=Array.flat();
     drawnItems.eachLayer(function(blayer){
     for (i in Array){
        if (blayer.id==Array[i]){
                blayer.setStyle({
            color: 'blue'   //or whatever style you wish to use;
        });
        }
    }

     });
     drawnSketchItems.eachLayer(function(slayer){
     for (i in Array){
        if (slayer.id==Array[i]){
            slayer.setStyle({
            color: 'blue'   //or whatever style you wish to use;
        });
        }
    }
   });

    }

    $('#saveSM').click(function(){
        sketchMap.pm.removeControls();
        allDrawnSketchItems[sketchMaptitle]=drawnSketchItems;
        allDrawnSketchItems["basemap"] = drawnItems;
        drawnSketchItems.setStyle({opacity:1});
        $( "#editmenuoptions" ).slideToggle(500);
        AlignmentArray[sketchMaptitle]=alignmentArraySingleMap;
        AlignmentArray[sketchMaptitle].id = id;
        AlignmentArray[sketchMaptitle].checkAlignnum = checkAlignnum;
        console.log(alignmentArraySingleMap);
        drawnItems.eachLayer(function(blayer){
        blayer.off('click');
        });

    });


function restoreBaseAlignment(alignmentArraySingleMap){

drawnItems.eachLayer(function(blayer){
    blayer.aligned = false;
    blayer.selected = false;
    $.each(alignmentArraySingleMap, function(i, item) {
        if(alignmentArraySingleMap[i].BaseAlign != null && Object.values(alignmentArraySingleMap[i].BaseAlign).includes(blayer.id)){
            blayer.aligned=true;
            console.log("restorealignment");
        }
    });
})

}

function checkIfAlignedAlready(alignSketchID){
drawnSketchItems.eachLayer(function(slayer){
$.each(alignmentArraySingleMap, function(i, item) {
    if(alignSketchID.includes(slayer.id) && (alignmentArraySingleMap[i].SketchAlign != null) && Object.values(alignmentArraySingleMap[i].SketchAlign).includes(slayer.id)){
     drawnItems.eachLayer(function(blayer){
     if((alignmentArraySingleMap[i].BaseAlign != null) && Object.values(alignmentArraySingleMap[i].BaseAlign).includes(blayer.id)){
        blayer.aligned=false;
     }
     });
     delete alignmentArraySingleMap[Object.keys(alignmentArraySingleMap)[i-1]];
     console.log("checkifalignedalready");
     styleLayers();
    }
    });
})


}


function styleLayers(){

if (drawnSketchItems){

    drawnSketchItems.eachLayer(function(slayer){
            if (slayer.selected){
                slayer.setStyle({weight:8});
            }
            if (!slayer.selected && !slayer.aligned){
                slayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a"});
            }
            if(!slayer.selected && slayer.aligned){
                slayer.setStyle({opacity:0.7,weight: 5,color: "#1a9eeb"});
            }
     });
}

if (drawnItems){
    drawnItems.eachLayer(function(blayer){

            if (blayer.selected){
                blayer.setStyle({weight:8});
            }
            if (!blayer.selected && !blayer.aligned){
                blayer.setStyle({opacity:1,weight: 5,color: "#e8913a"});
            }
            if(!blayer.selected && blayer.aligned){
                blayer.setStyle({opacity:1,weight: 5,color: "#1a9eeb"});
            }
     });
    }
}



function predictGenSingleLine(sketchtype,basetype){
var datatobesent = new L.geoJson();
 drawnItems.eachLayer(function(blayer){
    if((Object.keys(basetype).map(Number)).includes(blayer.id)){
       datatobesent.addData(blayer.toGeoJSON());
    }
});

var returnValue;

var url = "http://desktop-f25rpfv:8080/fmedatastreaming/GeneralizationPredict/junctiondetect.fmw?data=" + encodeURIComponent(JSON.stringify(JSON.stringify(datatobesent.toGeoJSON())));
var newurl = "http://desktop-f25rpfv:8080/fmerest/v3/repositories/GeneralizationPredict/networkcalculator.fmw/parameters?fmetoken=47e241ca547e14ab6ea961aef083f8a4cbe6dfe3"


var httpRequest = new XMLHttpRequest();
httpRequest.open("GET", url, false);
httpRequest.setRequestHeader("Authorization","fmetoken token=47e241ca547e14ab6ea961aef083f8a4cbe6dfe3")
httpRequest.setRequestHeader("Access-Control-Allow-Origin", "http://desktop-f25rpfv:8080");
httpRequest.setRequestHeader("Accept","text/html");
httpRequest.setRequestHeader("content-Type","application/x-www-form-urlencoded");
            httpRequest.onreadystatechange = function()
            {
                if (httpRequest.readyState == 4 && httpRequest.status == 200)
                {
                console.log(httpRequest.response);
                 var responseArray = (httpRequest.response).split(/\r?\n/);
                 responseArray.pop();
                 var nodeArray = [];
                  $.each(responseArray, function(i, item) {
                        nodeArray.push(Object.values(JSON.parse(responseArray[i])));
                  });
                 nodeArray = _.flatten(nodeArray,true);
                 if (new Set(nodeArray).size == nodeArray.length){
                    alert("Generalization Not possible");
                 }
                 else{
                    var nodeCount = _.countBy(nodeArray);
                    if (!(Object.values(nodeCount)).includes(3)){
                    returnValue =  "OmissionMerge";
                    console.log(returnValue);
                    }
                 }
                }
            }
            // send a request so we get a reply
            httpRequest.send();

 return returnValue;
}
