

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
var routeArray = [];
var sketchRouteArray = [];
var layerGroupBasemap = new L.LayerGroup();
var baseMap;
var drawnItems;



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
        layerGroupBasemap.addTo(baseMap);

    }

$( "#loaded" ).prop( "checked", true );
$( "#loaded" ).prop( "disabled", false );



}


 routeButton = L.easyButton('fa-arrow-trend-up',function(){

    drawnItems.eachLayer(function(blayer){
        blayer.on('click',function(e){
           if (!blayer.feature.properties.isRoute){
              routeArray.push(blayer.feature.properties.id);
              blayer.feature.properties.isRoute = "Yes";
              blayer.setStyle({
                color: 'red'   //or whatever style you wish to use;
            });
           }
           else if (blayer.feature.properties.isRoute == "Yes"){
                routeArray= routeArray.filter(function(item) {
                return item !== blayer.feature.properties.id;
                });
              blayer.feature.properties.isRoute = null ;
              blayer.setStyle({
                color: '#e8913a'   //or whatever style you wish to use;
            });
           }

        });

    });


 });





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
    var feature = layer.feature = layer.feature || {}; // Initialize feature
    feature.type = feature.type || "Feature"; // Initialize feature.type
    var props = feature.properties = feature.properties || {}; // Initialize feature.properties
    props.id = bid;
    props.isRoute = null;
    if(event.shape == "Polygon"){
    props.feat_type = "Landmark"
    }
    else{
    props.feat_type = null;}
    props.selected=false;
    props.aligned=false;
    props.otype = event.shape;
    drawnItems.addLayer(layer);
});


baseMap.pm.setGlobalOptions({
  pathOptions:{
    opacity:0.7,
    dashArray: [5, 5],
    weight: 5,
    color: "#e8913a",
    radius: 5},
  templineStyle: {
    color: "#e8913a",
    dashArray: [5, 5],
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
routeButton.addTo(baseMap);
});




$("#saveBM").click(function(){
$( "#marked" ).prop( "checked", true );
$( "#marked" ).prop( "disabled", false );
baseMap.pm.removeControls();
drawnItems.setStyle({opacity:1});

$( "#editmenuoptions" ).slideToggle(500);
drawnItems.eachLayer(function(blayer){
        blayer.off('click');
        });
baseMap.removeControl(routeButton);
    addClickBase();
});




function addClickBase(){
drawnItems.eachLayer(function(blayer){
        blayer.on('click',function(e){
        if(blayer.feature.properties.selected==false){
            blayer.feature.properties.selected=true;
            alignBaseID.push(blayer.feature.properties.id);
            baseOtypearray[blayer.feature.properties.id]=blayer.feature.properties.otype;
            styleLayers();
        }
        else{
            blayer.feature.properties.selected = false;
            alignBaseID= alignBaseID.filter(function(item) {
                return item !== blayer.feature.properties.id;
            })
            delete baseOtypearray[blayer.feature.properties.id];
            styleLayers();
        }
    });
    });
}


   $('.thumbnail').click(function(e){


        if (sketchMap != null) {
            sketchMap.remove();
            addClickBase();
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
        if(allDrawnSketchItems.hasOwnProperty(sketchMaptitle)){
        drawnSketchItems=allDrawnSketchItems[sketchMaptitle];
        drawnSketchItems.addTo(sketchMap);
        alignmentArraySingleMap=AlignmentArray[sketchMaptitle];
        id=AlignmentArray[sketchMaptitle].id+1;
        checkAlignnum = AlignmentArray[sketchMaptitle].checkAlignnum+1;
        restoreBaseAlignment(alignmentArraySingleMap);
        styleLayers();
        }
        else{
        drawnSketchItems = new L.geoJson().addTo(sketchMap);
        alignmentArraySingleMap={};
        drawnItems.eachLayer(function(blayer){
            blayer.feature.properties.selected=false;
            blayer.feature.properties.aligned=false;

        });
        styleLayers();
        id = 0;
        checkAlignnum = 1;
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
                radius: 5,
                dashArray: [5, 5],
                },
            templineStyle: {
                color: "#e8913a",
                dashArray: [5, 5],
             },
            hintlineStyle: {
                color: "#e8913a",
                dashArray: [5, 5],
            }
        });


        sketchMap.on('pm:create', function (event) {
            var layer = event.layer;

            var feature = layer.feature = layer.feature || {}; // Initialize feature
            feature.type = feature.type || "Feature"; // Initialize feature.type
            var props = feature.properties = feature.properties || {}; // Initialize feature.properties
            props.id = id;
            props.sid= 'S' + id;
            props.isRoute = null;
            props.mapType = "Sketch";
             if(event.shape == "Polygon"){
    props.feat_type = "Landmark"
    }
    else{
    props.feat_type = null;}
            props.selected = false;
            props.aligned = false;
            props.otype = event.shape;
            drawnSketchItems.addLayer(layer);
            id=id+1;

            layer.on('click', function (e) {
        if(layer.feature.properties.selected==false){
            layer.feature.properties.selected = true;
            alignSketchID.push(layer.feature.properties.sid);
            sketchOtypearray[layer.feature.properties.sid]=layer.feature.properties.otype;
            styleLayers();
            }
        else{
            layer.feature.properties.selected = false;
            alignSketchID= alignSketchID.filter(function(item) {
                return item !== layer.feature.properties.sid;
            });
            delete sketchOtypearray[layer.feature.properties.sid];
            styleLayers();
        }
        });



     });


    $( "#editmenuoptions" ).slideToggle(500);


    });



    $('#alignbutton').click(function(){
        checkIfAlignedAlready(alignSketchID);
        drawnItems.eachLayer(function(blayer){
        if (alignBaseID.includes(blayer.feature.properties.id)){
        blayer.feature.properties.aligned = true;
        blayer.feature.properties.selected = false;
        styleLayers();
        if (blayer.feature.properties.isRoute == "Yes"){
            drawnSketchItems.eachLayer(function(slayer){
                if (alignSketchID.includes(slayer.feature.properties.sid)){
                sketchRouteArray.push((slayer.feature.properties.sid).replace(/\D/g,''));
                slayer.feature.properties.isRoute = "Yes";
            }

            });
        }
        }
        });
        drawnSketchItems.eachLayer(function(slayer){
        if (alignSketchID.includes(slayer.feature.properties.sid)){
        slayer.feature.properties.aligned = true;
        slayer.feature.properties.selected = false;
        styleLayers();
        }
        });

        align(alignBaseID,alignSketchID,checkAlignnum,sketchOtypearray,baseOtypearray);
        checkAlignnum=checkAlignnum+1;
    });




    function align(BID,SID,num,sketchtype,basetype){
       var degreeOfGeneralization;
       var BaseAlign={};
       var SketchAlign={};
            BaseAlign[0]=BID;
            SketchAlign[0]=SID;
       console.log(BID.length);
       console.log(SID.length);
       degreeOfGeneralization=(BID.length - SID.length)/BID.length;
       console.log(degreeOfGeneralization);
       var genType;
       (async () => {
          genType = await predictGeneralization(sketchtype,basetype);
          alignmentArraySingleMap[num]={BaseAlign,SketchAlign,genType,degreeOfGeneralization};
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
    if((alignmentArraySingleMap[i].SketchAlign != null) && (alignmentArraySingleMap[i].SketchAlign[0]).includes(slayer.feature.properties.sid)){

    hoverarray.push(alignmentArraySingleMap[i].BaseAlign[0]);
    hoverarray.push(alignmentArraySingleMap[i].SketchAlign[0]);
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
                            return "No generalization";
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
        if (blayer.feature.properties.id==Array[i]){
                blayer.setStyle({
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

    $('#saveSM').click(function(){
        sketchMap.pm.removeControls();
        drawnItems.eachLayer(function(blayer){
        if (!blayer.feature.properties.aligned ){
          blayer.feature.properties.missing = true;
        }
        });
        allDrawnSketchItems[sketchMaptitle]=drawnSketchItems;
        allDrawnSketchItems["basemap"] = drawnItems;
        drawnSketchItems.setStyle({opacity:1});
        $( "#editmenuoptions" ).slideToggle(500);
        AlignmentArray[sketchMaptitle]=alignmentArraySingleMap;
        AlignmentArray[sketchMaptitle].id = id;
        AlignmentArray[sketchMaptitle].checkAlignnum = checkAlignnum;
        drawnItems.eachLayer(function(blayer){
        blayer.off('click');
        });

    });


function restoreBaseAlignment(alignmentArraySingleMap){

drawnItems.eachLayer(function(blayer){
    blayer.feature.properties.aligned = false;
    blayer.feature.properties.selected = false;
    $.each(alignmentArraySingleMap, function(i, item) {
        if(alignmentArraySingleMap[i].BaseAlign != null && (alignmentArraySingleMap[i].BaseAlign[0]).includes(blayer.feature.properties.id)){
            blayer.feature.properties.aligned=true;
        }
    });
})

hoverfunction();
}

function checkIfAlignedAlready(alignSketchID){
drawnSketchItems.eachLayer(function(slayer){
$.each(alignmentArraySingleMap, function(i, item) {
    if(alignSketchID.includes(slayer.feature.properties.sid) && (alignmentArraySingleMap[i].SketchAlign != null) && (alignmentArraySingleMap[i].SketchAlign[0]).includes(slayer.feature.properties.sid)){
     drawnItems.eachLayer(function(blayer){
     if((alignmentArraySingleMap[i].BaseAlign != null) && (alignmentArraySingleMap[i].BaseAlign[0]).includes(blayer.feature.properties.id)){
        blayer.feature.properties.aligned=false;
     }
     });
     delete alignmentArraySingleMap[Object.keys(alignmentArraySingleMap)[i-1]];
     styleLayers();
    }
    });
})


}


function styleLayers(){

if (drawnSketchItems){

    drawnSketchItems.eachLayer(function(slayer){
            if (slayer.feature.properties.selected){
                slayer.setStyle({weight:8});
            }
            if (!slayer.feature.properties.selected && !slayer.feature.properties.aligned && !slayer.feature.properties.isRoute){
                slayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: [5, 5]});
            }
            if (!slayer.feature.properties.selected && slayer.feature.properties.aligned && !slayer.feature.properties.isRoute){
                slayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: null});
            }
            if (!slayer.feature.properties.selected && !slayer.feature.properties.aligned && slayer.feature.properties.isRoute=="Yes"){
                slayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: [5, 5]});
            }
            if(!slayer.feature.properties.selected && slayer.feature.properties.aligned && slayer.feature.properties.isRoute=="Yes"){
                slayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: null,});
            }

     });
}

if (drawnItems){
    drawnItems.eachLayer(function(blayer){

         if (blayer.feature.properties.selected){
                blayer.setStyle({weight:8});
            }
            if (!blayer.feature.properties.selected && !blayer.feature.properties.aligned && !blayer.feature.properties.isRoute){
                blayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: [5, 5]});
            }
            if (!blayer.feature.properties.selected && blayer.feature.properties.aligned && !blayer.feature.properties.isRoute){
                blayer.setStyle({opacity:0.7,weight: 5,color: "#e8913a",dashArray: null});
            }
            if (!blayer.feature.properties.selected && !blayer.feature.properties.aligned && blayer.feature.properties.isRoute=="Yes"){
                blayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: [5, 5]});
            }
            if(!blayer.feature.properties.selected && blayer.feature.properties.aligned && blayer.feature.properties.isRoute=="Yes"){
                blayer.setStyle({opacity:0.7,weight: 5,color: "red",dashArray: null,});
            }
     });
    }
}



function predictGenSingleLine(sketchtype,basetype){
var datatobesent = new L.geoJson();
 drawnItems.eachLayer(function(blayer){
    if((Object.keys(basetype).map(Number)).includes(blayer.feature.properties.id)){
       datatobesent.addData(blayer.toGeoJSON());
    }
});

var returnValue;

var url = "http://desktop-f25rpfv:8080/fmedatastreaming/Generalization/junctiondetect.fmw?data=" + encodeURIComponent(JSON.stringify(JSON.stringify(datatobesent.toGeoJSON())));
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
                    }
                 }
                }
            }
            // send a request so we get a reply
            httpRequest.send();

 return returnValue;
}