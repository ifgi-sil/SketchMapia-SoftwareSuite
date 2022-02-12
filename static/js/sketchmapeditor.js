

var sketchMap;
var drawnSketchItems;
var alignSketchID=[];
var alignBaseID=[];

   $('.thumbnail').click(function(e){



        if (sketchMap != null) {
            sketchMap.remove();
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

   });




$('#drawSM').click(function(){

drawnSketchItems = new L.geoJson().addTo(sketchMap);

sketchMap.pm.addControls({
position: 'topleft',
drawCircle: false,
drawRectangle:false,
drawCircleMarker:false,
dragMode:false,
rotateMode:false,
cutPolygon:false
});

var id=0;
sketchMap.on('pm:create', function (event) {
    var layer = event.layer;
    layer.id='S'+id;
    drawnSketchItems.addLayer(layer);
    id=id+1;

layer.on('click', function (e) {
    alignSketchID.push(layer.id);
    console.log(alignSketchID);
    });




sketchMap.pm.setPathOptions({
  opacity:0.7,
  weight: 5
});


});

drawnItems.eachLayer(function(blayer){
blayer.on('click',function(e){
    alignBaseID.push(blayer.id);
    console.log(alignBaseID);
    return;
});
return;
});
$( "#editmenuoptions" ).slideToggle(500);
});


var saveSM = document.getElementById('saveSM');
saveBM.onclick = function(event) {
baseMap.pm.removeControls();


drawnItems.setStyle({opacity:1});
$( "#editmenuoptions" ).slideToggle(500);

}


var checkAlignnum=1;
$('#alignbutton').click(function(){

align(alignBaseID,alignSketchID,checkAlignnum);
checkAlignnum=checkAlignnum+1;

});


var AlignJSON={};

function align(BID,SID,num){

var sketchmapAlign = "SketchMap"+num;
var basemapAlign = "BaseMap"+num;

for (var i = 1; i < BID.length; i++) {
    var objName = 'Obj' + i;
    var objValue = BID[i];

}

}



