
var DEST_ADDRESS = "";

var MAP_MARKER;

window.continue_countdown = true;
function countdown(val, stepfunc, afterfunc){
    if (!window.continue_countdown){
        return;
    }
    stepfunc(val);
    if (val == 0){
        afterfunc();
    } else {
        setTimeout(function(){countdown(val-1, stepfunc, afterfunc);}, 1000);
    }
}


function createMap(inputData){
    var myLatlong = new google.maps.LatLng (inputData.latitude, inputData.longitude);
    
    var mapOptions = {
        center: myLatlong,
        zoom: 16
    };
    
    var map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

    MAP_MARKER = new google.maps.Marker({
        animation: google.maps.Animation.DROP,
        position: myLatlong,
        map: map,
        title: "Where Leland is."
    });
    displayAge(inputData);
};

function displayAge(inputData){
    // Get current time in seconds as epoch
    var now = (new Date()).getTime() / 1000;
    var timeDiff = now - inputData.monotonic_timestamp;
    var minuteDiff = timeDiff / 60.0;
    var updateDiv = $('#last-updated-minutes');

    updateDiv.text(minuteDiff.toFixed(2));
};

function updateTravelInfo(){
    // Get the new travel distance info and update the div containing the
    // time-to-place information.
    if (!DEST_ADDRESS) {
        return;
    }
    var distElem = $('#dist-display');

    // If the distance element doesn't exist, create it.
    if (distElem.length == 0) {
        distElem = $('<p id="dist-display"/>');
        $('#dest-query-button').after(distElem);
    }
    $.ajax({
        url: '/time_to_place/'+DEST_ADDRESS,
        dataType: 'json',
        success: function(data) {
            console.log('Updating travel info', DEST_ADDRESS);
            var travel_time = data['rows'][0]['elements'][0]["duration"]["text"];
            distElem.text('It will be '+travel_time+' minutes to '+DEST_ADDRESS+'.');
        }
    })
}



function updateMarker(){
    // Updates the marker with the most recent location from the device
    $.ajax({
        url: '/currentpos',
        dataType: 'json',
        success: function(data) {
            var latLng = new google.maps.LatLng(data.latitude, data.longitude);
            MAP_MARKER.setPosition(latLng);
            displayAge(data);
        }
    });
}

function startTimer(){
    countdown(60, function(curTime){
        $('#marker-update-countdown').text('Map will update in: '+String(curTime));
    }, function(){
        updateMarker();
        startTimer();
        updateTravelInfo();
    });
}


function initialize() {
    $.ajax({
        url: '/currentpos',
        dataType: 'json',
        success: createMap
    });
    startTimer();
    $('#dest-query-button').bind('click', function(){
        DEST_ADDRESS = $('#dest-address').val();
        updateTravelInfo();
    });
};


google.maps.event.addDomListener(window, 'load', initialize);

