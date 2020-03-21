$(document).ready(function() {
    $('#nav-numberofworkers').siblings().removeClass('active');
    $('#nav-numberofworkers').addClass('active');
    shownumberofworkers()
});

function shownumberofworkers() {
 $.ajax({
        type: 'POST',
        url: '/fetch_number_of_workers',
        data: '',
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function() {
            $('#charts3').html("<img class='loading' src='static/img/loading.gif'>");
        },
        success: function(data) {
            data = JSON.parse(data);
            newdata = []
            for (i=0 ; i<data.length ; i++){
                name = data[i].name
                info = JSON.parse(data[i].data)
                newdata.push({
                    "name": name,
                    "data": info
                })
            }

            var myChart3 = Highcharts.stockChart('charts3', {
                legend: {
                        enabled: true,
                        align: 'right',
                },

                rangeSelector: {
                    selected: 1
                },

                title: {
                    text: 'Number of Workers'
                },

                series: newdata
            });
        },
        error: function(xhr, textStatus, error){
            $('#charts3').html("");
            showAlert("Unable to show the charts 1", "alert-danger")
            console.log(error)
        }
    });
}