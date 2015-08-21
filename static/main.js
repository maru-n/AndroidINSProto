// Sensor Data Chart (amcharts.js)
var ws_url = "ws://" + location.host + "/ws";
var ws = new WebSocket(ws_url);
var accel_chart;
var angr_chart;
var mag_chart;
var chartCursor;

// Attitude Display (three.js)
var scene, camera, renderer;
var cube;
var renderSizeWidth = window.innerWidth;
var renderSizeHeight = window.innerHeight;


ws.onopen = function() {};

ws.onmessage = function (evt) {
    var data = JSON.parse(evt.data)

    if (data.result == "successed") {
        $("#time").text(data.time + " sec");
        $("#message").text("");
        accel_chart.dataProvider.push({
            'time': data.time,
            'x': data.accel[0],
            'y': data.accel[1],
            'z': data.accel[2]
        });
        accel_chart.validateData();
        angr_chart.dataProvider.push({
            'time': data.time,
            'x': data.angr[0],
            'y': data.angr[1],
            'z': data.angr[2]
        });
        angr_chart.validateData();
        mag_chart.dataProvider.push({
            'time': data.time,
            'x': data.mag[0],
            'y': data.mag[1],
            'z': data.mag[2]
        });
        mag_chart.validateData();
    }else{
        $("#message").text(data.message);
    }
};

AmCharts.ready(function () {
    accel_chart = new AmCharts.AmSerialChart();
    accel_chart = make_xyz_chart();
    accel_chart.write("accel-chart");

    angr_chart = new AmCharts.AmSerialChart();
    angr_chart = make_xyz_chart();
    angr_chart.write("angr-chart");

    mag_chart = new AmCharts.AmSerialChart();
    mag_chart = make_xyz_chart();
    mag_chart.write("mag-chart");
});

function make_xyz_chart() {
    var chart = new AmCharts.AmSerialChart();
    chart.dataProvider = [];
    chart.categoryField = "time";
    chart.balloon.bulletSize = 5;

    var valueAxis = new AmCharts.ValueAxis();
    chart.addValueAxis(valueAxis);

    for (var i = 0; i < 3; i++) {
        var graph = new AmCharts.AmGraph();
        graph.hideBulletsCount = 50;
        graph.bullet = "round";
        graph.bulletColor = "#FFFFFF";
        graph.useLineColorForBulletBorder = true
        graph.bulletBorderAlpha = 1;
        chart.addGraph(graph);
    }

    chart.graphs[0].valueField = "x";
    chart.graphs[0].lineColor = "red";
    chart.graphs[1].valueField = "y";
    chart.graphs[1].lineColor = "green";
    chart.graphs[2].valueField = "z";
    chart.graphs[2].lineColor = "blue";
    chart.addGraph(graph);

    var chart_scrollbar = new AmCharts.ChartScrollbar();
    chart.addChartScrollbar(chart_scrollbar);

    return chart;
}

function init_tree() {
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera( 75, renderSizeWidth/renderSizeHeight, 1, 10000 );
    camera.position.z = 1000;

    cube = new THREE.Mesh(
        new THREE.BoxGeometry( 200, 200, 200 ),
        new THREE.MeshBasicMaterial({
            color: 0xff0000,
            wireframe: true
        }));

    scene.add( cube );

    cube.useQuaternion = true;
    cube.quaternion =  new THREE.Quaternion(0,0,0,0);

    renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );

    document.body.appendChild( renderer.domElement );
}

$(function(){
    init_tree();
});
