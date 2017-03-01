$(function () {
    $('#sendSerie').click(function () {
        var results = $('#results');
        results.empty();
        $.ajax({
            url: '/show_series/get/',
            data: $('form').serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                var deck = $('<div/>', {"class": "card-deck"}).attr("id", "deck0");
                deck.after($('<p/>'));
                var i = 0;
                $.each(response, function (index, val) {
                    if ((index % 5) == 0) {
                        deck = $('<div/>', {"class": "card-deck"}).attr("id", "deck" + i);
                        results.append(deck);
                        results.append("<p></p>")
                        i++;
                    }

                    var card = $('<div/>', {
                        "class": "card"
                    });

                    card.append($('<img/>', {
                        "class": "card-img-top img-fluid",
                        "src": val.image
                    }));

                    var cardblock = $('<div/>', {
                        "class": "card-block"
                    });

                    cardblock.append($('<h6/>', {
                        "class": "card-title"
                    }).text(val.title));

                    cardblock.append($('<h6/>', {
                        "class": "card-text text-muted"
                    }).text(val.prezzo));

                    var date = new Date(val.data);
                    var issuedate = date.getDate() + '/' + (date.getMonth() + 1) + '/' + date.getFullYear();

                    cardblock.append($('<h6/>', {
                        "class": "card-text text-muted"
                    }).text(issuedate));

                    cardblock.appendTo(card);

                    var addButton = $('<button/>', {
                        "class": "btn btn-sm btn-primary",
                        "id": "btn" + index,
                        "type": "button",
                        "name": "add",
                        "issue": val.title
                    }).text("Aggiungi");
                    addButton.on("click","#btn"+index, addSerie);
                    card.append(addButton);

                    var remButton = $('<button/>', {
                        "class": "btn btn-sm btn-danger",
                        "id": "btn" + index,
                        "type": "button",
                        "name": "remove"
                    }).text("Rimuovi");
                    card.append(remButton);
                    card.appendTo(deck);
                    // console.log(val.title);
                });
            },
            error: function (error) {
                console.log(error)
            }
        });
    });
});

function addSerie() {
    $.ajax({
        url: '/show_series/add_issue/',
        data: $(this).attr("issue"),
        type: 'POST',
        dataType: 'json',
        success: function (response) {
            console.log(response);
            alert("sent " + data);
        },
        error: function (error) {
            console.log(error)
        }
    });
}