
var DEST_ADDRESS = "";

var MAP_MARKER;
var HAS_DRAGGED = false;

window.continue_countdown = true;
/*
 * Create a "countdown", taking a starting value, a function to call on each
 * decrement of that value, and a function to be called once that value is
 * zero. The value is decremented and this function recurses every 1000
 * milliseconds, until the value is zero.
 */
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

/*
 * Create an instance of a Google map and populate it with the provided
 * `inputData`. Additionally, update the div displaying the age of the latest
 * datapoint/current marker.
 */
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
    google.maps.event.addListener(map, 'dragend', function(){HAS_DRAGGED = true;});
    displayAge(inputData);
};

/*
 * Update the display of the age of the latest data, in minutes.
 */
function displayAge(inputData){
    // Get current time in seconds as epoch
    var now = (new Date()).getTime() / 1000;
    var timeDiff = now - inputData.monotonic_timestamp;
    var minuteDiff = timeDiff / 60.0;
    var updateDiv = $('#last-updated-minutes');

    updateDiv.text(minuteDiff.toFixed(2));
};

/*
 * Get the new travel distance info and update the div containing the
 * time-to-place information.
 */
function updateTravelInfo(){
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
        url: '/api/v1/time_to_place/'+DEST_ADDRESS,
        dataType: 'json',
        success: function(data) {
            console.log('Updating travel info', DEST_ADDRESS);
            var travel_time = data['rows'][0]['elements'][0]["duration"]["text"];
            distElem.text('It will be '+travel_time+' to '+DEST_ADDRESS+'.');
        }
    })
}

function drawHistory() {
    var time_difference = 36000;
    $.ajax({
        url: '/api/v1/currentpos',
        dataType: 'json',
        success: function(data) {
            var latest_time = parseInt(data['monotonic_timestamp'], 10);
            var start_range = latest_time - time_difference;
            $.ajax({
                url: '/api/v1/data_range/'+start_range+'/'+latest_time,
                dataType: 'json',
                success: function(entries) {
                    var coords = [];
                    for (var i = 0; i < entries.length; i++) {
                        var entry = entries[i];
                        var latLng = new google.maps.LatLng(entry.latitude, entry.longitude);
                        coords.push(latLng);
                    }
                    var travelPath = new google.maps.Polyline({
                        path: coords,
                        geodesic: true,
                        strokeColor: '#FF0000',
                        strokeOpacity: 1.0,
                        strokeWeight: 2
                    });
                    travelPath.setMap(MAP_MARKER.map);
                }
            });
        }
    });
}


/*
 * Updates the marker with the most recent location from the device
 */
function updateMarker(){
    $.ajax({
        url: '/api/v1/currentpos',
        dataType: 'json',
        success: function(data) {
            var latLng = new google.maps.LatLng(data.latitude, data.longitude);
            MAP_MARKER.setPosition(latLng);
            if (!HAS_DRAGGED) {
                MAP_MARKER.map.panTo(latLng);
            }
            displayAge(data);
        }
    });
}

/*
 * Starts the countdown timer, and provide a function to update the remaining
 * seconds in the countdown, and a function to update the entire map display
 * state once the timer reaches zero.
 */
function startTimer(){
    countdown(30, function(curTime){
        $('#marker-update-countdown').text('Map will update in: '+String(curTime));
    }, function(){
        updateMarker();
        startTimer();
        updateTravelInfo();
    });
}


function initialize() {
    $.ajax({
        url: '/api/v1/currentpos',
        dataType: 'json',
        success: createMap
    });
    drawHistory();
    startTimer();
    $('#dest-query-button').bind('click', function(){
        DEST_ADDRESS = $('#dest-address').val();
        updateTravelInfo();
    });
};


google.maps.event.addDomListener(window, 'load', initialize);

