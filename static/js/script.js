$(function () {
    $('#sendSerie').click(function () {
        // var user = $('#txtUsername').val();
        // var pass = $('#txtPassword').val();
        var serie = $('#selectSerie').val();
        $('#results').empty();
        $.ajax({
            url: '/show_series/get/',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                $.each(response, function (index, val) {
                    $("#results").append(
                        $('<div/>', {"class": "card"}).append(
                            $('<img/>', {"class": "card-img-top img-fluid", "src": val.image}).add(
                                $('<div/>', {"class": "card-block"}).append(
                                    $('<div/>', {"class": "card-text"}).text(val.title)
                                ).append(
                                    $('<h6/>').text(val.subtitle)
                                ).append(
                                    $('<h6/>').text(val.data)
                                ).append(
                                    $('<h6/>').text(val.prezzo)
                                )
                            )
                        )
                    );
                    console.log(val.title);
                });
            },
            error: function (error) {
                console.log(error)
            }
        });
    });
});