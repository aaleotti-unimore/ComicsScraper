/**
 * Created by archeffect on 08/02/17.
 */
$(function () {
    $('#sendSerie').click(function () {
        // var user = $('#txtUsername').val();
        // var pass = $('#txtPassword').val();
        var serie = $('#selectSerie').val();
        $.ajax({
            url: '/show_series/get/',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                // console.log(response);
                var json_obj = $.parseJSON(response);
                console.log(json_obj[0].title)

                $('span').html(json_obj[0].title);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});