$(function () {
    var results = $('#results');
    $('#sendSerie').click(function () {
        var n_columns = 5;
        var results = $('#results');
        results.empty();
        // console.log("sent " + $('form').serialize());
        $.ajax({
            url: '/show_series/get/',
            data: $('#formSerie').serialize(),
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
                var deck = $('<div/>', {"class": "card-deck"}).attr("id", "deck0");
                deck.after($('<p/>'));
                var n = 0;
                $.each(response, function (index, val) {
                    val.specials = 0;
                    val.index = index;
                    if (val.title != null) {
                        var title = val.title.replace(/[^\w\s]/gi, '').split(' ').join('-');
                        // console.log("#mod-" + title);
                    }
                    if ((index % 5) == 0) {
                        deck = $('<div/>', {"class": "card-deck"}).attr("id", "deck" + n);
                        results.append(deck);
                        results.append("<p></p>");
                        i++;
                    }
                    var html = Handlebars.templates.card(val);
                    deck.append(html);
                    var modal = $('#response');
                    modal.modal({
                        focus: true,
                        show: false
                    });
                    $('#btn-sum-' + index).click(function () {
                        $('#mod-' + index).modal();
                    });
                    $('#btn-add-' + index).click(function () {
                        console.log("sent for adding" + val.title);
                        $.ajax({
                            url: '/user/add_special_issue/',
                            data: {special_issue: val.title},
                            type: 'POST',
                            dataType: 'json',
                            success: function (response) {
                                // modal.empty();
                                modal.find(".modal-body").text(response.content);
                                modal.modal('show');
                                console.log("success" + response.content)
                            }
                        })
                    });
                    $('#btn-del-' + index).click(function () {
                        console.log("sent for remove " + val.title);
                        $.ajax({
                            url: '/user/remove_special_issue/',
                            data: {special_issue: val.title},
                            type: 'POST',
                            dataType: 'json',
                            success: function (response) {
                                alert(response.content);
                                console.log("success" + response)
                            }
                        })
                    })
                });


            },
            error: function (error) {
            }
        })
    })
});

