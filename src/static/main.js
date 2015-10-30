var accel_data, angr_data, mag_data
var accel_chart, angr_chart, mag_chart;
var xyz_chart_option;
const MAX_DATAPOINT_NUM = 100

function init_sensor_data_charts(accel_element_id, angr_element_id, mag_element_id) {
    xyz_chart_option = {
        colors: ['red', 'green', 'blue'],
        legend: 'none'
    };

    accel_data = new google.visualization.DataTable();
    accel_data.addColumn('number', 'time');
    accel_data.addColumn('number', 'x');
    accel_data.addColumn('number', 'y');
    accel_data.addColumn('number', 'z');

    angr_data = new google.visualization.DataTable();
    angr_data.addColumn('number', 'time');
    angr_data.addColumn('number', 'x');
    angr_data.addColumn('number', 'y');
    angr_data.addColumn('number', 'z');

    mag_data = new google.visualization.DataTable();
    mag_data.addColumn('number', 'time');
    mag_data.addColumn('number', 'x');
    mag_data.addColumn('number', 'y');
    mag_data.addColumn('number', 'z');

    accel_chart = new google.visualization.LineChart(document.getElementById(accel_element_id));
    angr_chart = new google.visualization.LineChart(document.getElementById(angr_element_id));
    mag_chart = new google.visualization.LineChart(document.getElementById(mag_element_id));
}

function update_sensor_data_charts(data) {
    accel_data.addRow([data.time, data.acceleration[0], data.acceleration[1], data.acceleration[2]]);
    if (accel_data.getNumberOfRows() > MAX_DATAPOINT_NUM) {
        accel_data.removeRow(0);
    }
    accel_chart.draw(accel_data, xyz_chart_option);
    angr_data.addRow([data.time, data.angular_rate[0], data.angular_rate[1], data.angular_rate[2]]);
    if (angr_data.getNumberOfRows() > MAX_DATAPOINT_NUM) {
        angr_data.removeRow(0);
    }
    angr_chart.draw(angr_data, xyz_chart_option);
    mag_data.addRow([data.time, data.magnetic[0], data.magnetic[1], data.magnetic[2]]);
    if (mag_data.getNumberOfRows() > MAX_DATAPOINT_NUM) {
        mag_data.removeRow(0);
    }
    mag_chart.draw(mag_data, xyz_chart_option);

}


var renderer, scene, camera, cube;

function init_attitude_display(element_id) {
    var $target = $('#'+element_id);
    $target.empty();
    var renderSize = $target.width();
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera( 75, 1, 1, 10000 );
    camera.position.z = 1000;

    cube = new THREE.Mesh(
        new THREE.BoxGeometry( 600, 600, 300 ),
        new THREE.MeshBasicMaterial({
            color: 0xff0000,
            wireframe: true
        }));

    scene.add( cube );

    cube.quaternion =  new THREE.Quaternion(0,0,0,0);

    renderer = new THREE.WebGLRenderer();
    renderer.setSize( renderSize, renderSize );
    renderer.setClearColor( 0xffffff );

    $target.append(renderer.domElement);
}

function update_attitude_display(data) {
    var qtn = data.quaternion;
    cube.quaternion.set(qtn[0], qtn[1], qtn[2], qtn[3]);
    renderer.render(scene, camera);
}

var renderer_p, scene_p, camera_p;
var $data_string_area
function init_navigation_display(element_id) {
    var $target = $('#'+element_id);
    $target.empty();

    $data_string_area = $('<div></div>');
    $target.append($data_string_area);

    var target_width = $target.width();
    var width = target_width;
    var height = 500;
    scene_p = new THREE.Scene();

    var material = new THREE.LineBasicMaterial({
        color: 0x666666
    });
    const GRID_RANGE = 20;
    const GRID_TICK = 1;
    for (var i = -GRID_RANGE; i<=GRID_RANGE; i+=GRID_TICK){
        for (var j = -GRID_RANGE; j<=GRID_RANGE; j+=GRID_TICK){
            var geometry = new THREE.Geometry();
            geometry.vertices.push(
                new THREE.Vector3( i+GRID_TICK, j, 0 ),
                new THREE.Vector3( i, j, 0 ),
                new THREE.Vector3( i, j+GRID_TICK, 0 )
                );
            var line = new THREE.Line( geometry, material );
            scene_p.add(line);
        }
    }

    camera_p = new THREE.PerspectiveCamera( 45, width/height, 1, 10000 );
    camera_p.position.z = 5;

    renderer_p = new THREE.WebGLRenderer();
    renderer_p.setSize( width, height );
    renderer_p.setClearColor( 0xffffff );

    $target.append(renderer_p.domElement);

    scene_p.add(positionMarker);
}

var trackCircleGeometry = new THREE.CircleGeometry( 0.01, 8 );
var trackCircleMaterial = new THREE.MeshBasicMaterial({color: 0x0099ff});
var positionMarker = new THREE.Mesh(
    new THREE.CircleGeometry( 0.05, 8 ),
    new THREE.MeshBasicMaterial({color: 0x0000ff})
);

function update_navigation_display(data) {
    var pos = data.position;
    var vel = data.velocity;
    var dv = data.delta_velocity;
    // pos is NED frame and display North->y, East->x, Down->z
    var pos_north = pos[0];
    var pos_east  = pos[1];
    var newTrackCircle = new THREE.Mesh( trackCircleGeometry, trackCircleMaterial );
    newTrackCircle.position.x = pos_east;
    newTrackCircle.position.y = pos_north;
    //newTrackCircle.position.z = pos[2];
    scene_p.add(newTrackCircle);

    positionMarker.position.x = pos_east;
    positionMarker.position.y = pos_north;

    camera_p.position = newTrackCircle.position
    renderer_p.render(scene_p, camera_p);

    var data_html = "dvx:" + dv[0]  + " dvy:" + dv[1]  + " vz: " + dv[2]  + "<br/>" +
                    "vx:"  + vel[0] + " vy:"  + vel[1] + " vz: " + vel[2] + "<br/>" +
                    "x:"   + pos[0] + " y:"   + pos[1] + " z: "  + pos[2] + "<br/>";

    $data_string_area.html(data_html);
}


var time = 0.0;

function update() {
    $.get('/alldata', function(data){
        var data = JSON.parse(data)
        if (data.result == "successed") {
            update_sensor_data_charts(data);
            update_attitude_display(data);
            update_navigation_display(data);

            var newTime = data.time;
            $("#time").text(newTime.toFixed(2));
            var fps = 1.0 / (newTime - time);
            $("#fps").text(fps.toFixed(1));
            time = newTime;
            $("#message").text("");

        }else{
            $("#message").text(data.message);
        }
        setTimeout(update, 0);
    });
}


$(function(){
    init_sensor_data_charts('accel-chart', 'angr-chart', 'mag-chart');
    init_attitude_display('attitude-data-area');
    init_navigation_display('navigation-data-area');
    $("#reset-btn").click(function(){
      $.post('/resetdata', function(data){
        init_sensor_data_charts('accel-chart', 'angr-chart', 'mag-chart');
        init_attitude_display('attitude-data-area');
        init_navigation_display('navigation-data-area');
      });
    });
    update();
});
