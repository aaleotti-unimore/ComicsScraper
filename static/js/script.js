$(function () {
    var results = $('#results');
    $('#sendSerie').click(function () {
        var n_columns = 5;
        var results = $('#results');
        results.empty();
        $.ajax({
            url: '/show_series/get/',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                var length = response.length;
                var rest = length % n_columns;
                if (rest != 0) {
                    var itera = (n_columns * (Math.floor(length / n_columns) + 1) - length);
                    for (var i = 0; i < itera; i++) {
                        response.push({})
                    }
                }
                // console.log("after: " + response.length);
                // console.log(response);
                var source = $("#card-template").html();
                var template = Handlebars.compile(source);
                var deck = $('<div/>', {"class": "card-deck"}).attr("id", "deck0");
                deck.after($('<p/>'));
                var n = 0;
                $.each(response, function (index, val) {
                    if (val.title != null) {
                        var title = val.title.split(' ').join('-');
                    }
                    if ((index % 5) == 0) {
                        deck = $('<div/>', {"class": "card-deck"}).attr("id", "deck" + n);
                        results.append(deck);
                        results.append("<p></p>");
                        i++;
                    }
                    var html = template(val);
                    deck.append(html);
                    $('#btn-' + title).click(function () {
                        console.log("#mod-" + title);
                        $('#mod-'+title).modal();
                    })
                });


            },
            error: function (error) {
            }
        })
    })
});