$(document).ready(function() {
    $('#nav-configure').siblings().removeClass('active');
    $('#nav-configure').addClass('active');
    $("button[class~='btn-success']").each(function (i, ele) {
        // console.log(ele)
        $(ele).on("click", function(e){
            e.preventDefault();
            modifyEnable($(ele).attr('id'));
        });
    });
    $('#clear_btn').on("click", function() {
        clear_data()
    });
    $('#stop_btn').on("click", function() {
        stop_manager_terminate_intances()
    });
});

function modifyEnable(id) {
    // console.log(id)
    if (id == "modify-btn1") {
        $("#input1").prop('readonly', false);
    } else if (id == "modify-btn2") {
        $("#input2").prop('readonly', false);
    } else if (id == "modify-btn3") {
        $("#input3").prop('readonly', false);
    } else if (id == "modify-btn4") {
        $("#input4").prop('readonly', false);
    } else {}
}

function clear_data() {
    $.ajax({
        type: 'POST',
        url: '/clear_data',
        data: '',
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function() {
            $('#clear_btn').html("Clearing <img class='ajax-loading' src='static/img/ajax-loading.gif'>")
            $('#clear_btn').prop("disabled", true)
        },
        success: function(data) {
            data = JSON.parse(data);
            if(data.flag == true) {
                msg = 'All data cleared.'
                showAlert_clear(msg, 'alert-success')
            } else {
                showAlert_clear(data.msg, 'alert-danger')
            }
            $('#clear_btn').html("Clear")
            $('#clear_btn').prop("disabled", false)
        },
        error: function(xhr, textStatus, error){
            showAlert_clear("Unable to clear data", "alert-danger")
            $('#clear_btn').html("Clear")
            $('#clear_btn').prop("disabled", false)
            console.log(error)
        }
    });
}

function stop_manager_terminate_intances() {
    $.ajax({
        type: 'POST',
        url: '/stop_manager_terminate_intances',
        data: '',
        contentType: false,
        cache: false,
        processData: false,
        beforeSend: function() {
            $('#stop_btn').html("Stoping <img class='ajax-loading' src='static/img/ajax-loading.gif'>")
            $('#stop_btn').prop("disabled", true)
        },
        success: function(data) {
            data = JSON.parse(data);
            if(data.flag == true) {
                msg = 'All workers and manager are stopped.'
                showAlert_stop(msg, 'alert-success')
            } else {
                showAlert_stop(data.msg, 'alert-danger')
            }
            $('#stop_btn').html("Stop")
            $('#stop_btn').prop("disabled", false)
        },
        error: function(xhr, textStatus, error){
            showAlert_stop("Unable to stop", "alert-danger")
            $('#stop_btn').html("Stop")
            $('#stop_btn').prop("disabled", false)
            console.log(error)
        }
    });
}

function showAlert_clear(msg, type) {
    if (type == 'alert-warning') {
        title = "Warning: "
    } else if (type == 'alert-success') {
        title = "Success: "
    } else if (type == 'alert-danger') {
        title = "Failure: "
    } else { return ''}

    msg = "<strong>" + title + "</strong>" + msg
    alert = "<div class='alert " + type + " alert-dismissible fade show' role='alert'>" + msg
    alert += "<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span>"
    alert += "</button></div>"
    $('#msg').html(alert)
}

function showAlert_stop(msg, type) {
    if (type == 'alert-warning') {
        title = "Warning: "
    } else if (type == 'alert-success') {
        title = "Success: "
    } else if (type == 'alert-danger') {
        title = "Failure: "
    } else { return ''}

    msg = "<strong>" + title + "</strong>" + msg
    alert = "<div class='alert " + type + " alert-dismissible fade show' role='alert'>" + msg
    alert += "<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span aria-hidden='true'>&times;</span>"
    alert += "</button></div>"
    $('#msg_stop').html(alert)
}

