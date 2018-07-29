function activity_chart(chart_data) {
    new Morris.Line({
        element: 'activity',

        data: chart_data.data,

        xkey: chart_data.xkey,
        ykeys: chart_data.ykeys,
        labels: chart_data.labels,
        lineWidth: 0,
        pointSize: 5,
        postUnits: 's'
    });
}

function water_chart(chart_data, throughput) {
    var pumped_water = [];
    var total_water = 0;
    for (var i = 0; i < chart_data.data.length; i++) {
        var pumped = chart_data.data[i].active * throughput;
        total_water += pumped;
        pumped_water.push({timeStamp: chart_data.data[i].timeStamp, pumped: pumped.toFixed(2), total: total_water.toFixed(2)});
    }

    new Morris.Line({
        element: 'water',

        data: pumped_water,
        xkey: 'timeStamp',
        ykeys: ['pumped', 'total'],
        labels: ['Pumped Water', 'Total Amount'],
        lineWidth: 1,
        pointSize: 5,
        postUnits: 'l'
    });

    document.getElementById("total_water").innerHTML = String(total_water.toFixed(2)) + " l";
}

function energy_chart(chart_data, power, voltage) {
    var consume = [];
    var total_consume = 0;
    for (var i = 0; i < chart_data.data.length; i++) {
        var consumed = chart_data.data[i].active * (power / voltage) * (5 / 18);
        consumed += (4 + chart_data.data[i].active ) * (5 / 18) * 0.1;
        total_consume += consumed;
        consume.push({timeStamp: chart_data.data[i].timeStamp, consumed: consumed.toFixed(2), total: total_consume.toFixed(2)});
    }

    new Morris.Line({
        element: 'energy',
        data: consume,
        xkey: 'timeStamp',
        ykeys: ['consumed', 'total'],
        labels: ['Consumed Energy', 'Total Amount'],
        lineWidth: 1,
        pointSize: 5,
        postUnits: 'mAh'
    });

    document.getElementById("total_energy").innerHTML = String(total_consume.toFixed(2)) + " mAh";
}

function overview_charts(url) {
    var xhttp = new XMLHttpRequest();
    var csrftoken = getCookie('csrftoken');
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {
                var jsonData = JSON.parse(xhttp.responseText);
                activity_chart(jsonData);
            }
            else {
                console.log("Received response with status code: " + String(this.status));
                alert("Failed to load chart data");
                return null;
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send();
}

function pump_details_charts(url, throughput, power, pump_voltage) {
    var xhttp = new XMLHttpRequest();
    var csrftoken = getCookie('csrftoken');
    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200) {
                var jsonData = JSON.parse(xhttp.responseText);
                activity_chart(jsonData);
                water_chart(jsonData, throughput);
                energy_chart(jsonData, power, pump_voltage);
            }
            else {
                console.log("Received response with status code: " + String(this.status));
                alert("Failed to load chart data");
                return null;
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send();
}