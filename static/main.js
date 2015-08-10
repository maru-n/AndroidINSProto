var ws_url = "ws://" + location.host + "/ws";
console.log(ws_url);
var ws = new WebSocket(ws_url);
var accel_chart;
var chartCursor;


ws.onopen = function() {};

ws.onmessage = function (evt) {
    var data = JSON.parse(evt.data)
    if (data.result == "successed") {
        $("#time").text(data.time + " sec");
        //$("#accel").text("x:" + data.accel[0] + "y:" + data.accel[1] + "z:" + data.accel[2]);
        $("#gyro").text("x:" + data.gyro[0] + "y:" + data.gyro[1] + "z:" + data.gyro[2]);
        $("#mag").text("x:" + data.mag[0] + "y:" + data.mag[1] + "z:" + data.mag[2]);
        $("#message").text("");
        accel_chart.dataProvider.push({
            'time': data.time,
            'accel-x': data.accel[0],
            'accel-y': data.accel[1],
            'accel-z': data.accel[2]
        });
        accel_chart.validateData();
    }else{
        $("#message").text(data.message);
    }
};

AmCharts.ready(function () {

    accel_chart = new AmCharts.AmSerialChart();

    accel_chart.dataProvider = [];
    accel_chart.categoryField = "time";
    accel_chart.balloon.bulletSize = 5;


    var valueAxis = new AmCharts.ValueAxis();
    accel_chart.addValueAxis(valueAxis);

    for (var i = 0; i < 3; i++) {
        var graph = new AmCharts.AmGraph();
        graph.hideBulletsCount = 50;
        graph.bullet = "round";
        graph.bulletColor = "#FFFFFF";
        graph.useLineColorForBulletBorder = true
        graph.bulletBorderAlpha = 1;
        accel_chart.addGraph(graph);
    }

    accel_chart.graphs[0].valueField = "accel-x";
    accel_chart.graphs[0].lineColor = "red";
    accel_chart.graphs[1].valueField = "accel-y";
    accel_chart.graphs[1].lineColor = "green";
    accel_chart.graphs[2].valueField = "accel-z";
    accel_chart.graphs[2].lineColor = "blue";
    accel_chart.addGraph(graph);

    var chartScrollbar = new AmCharts.ChartScrollbar();
    accel_chart.addChartScrollbar(chartScrollbar);

    accel_chart.write("accel-chart");
});


