/**
 * Created by archeffect on 22/03/17.
 */
$(document).ready(getSpecials());

function getSpecials() {
    $.ajax({
        url: '/',
        type: 'POST',
        dataType: 'json',
        success: function (response) {
            var deck = $('#specials_block');
            $.each(response.special_issues, function (index, val) {
                val.specials = 1;
                val.index = index;
                var html = Handlebars.templates.card(val);
                deck.append(html);
                deck.append("<p></p>");
                $("#specials_footer").text("Totale € " + response.special_issues_sum);
                $('#btn-sum-' + index).click(function () {
                    $('#mod-' + index).modal();
                });
                $('#btn-del-' + index).click(function () {
                    console.log("sent for remove " + val.title);
                    $.ajax({
                        url: '/user/remove_special_issue/',
                        data: {special_issue: val.title},
                        type: 'POST',
                        dataType: 'json',
                        success: function (response) {
                            $(this).parents('.card').remove()
                            deck.empty();
                            deck.append("<h3 class=\"card-title\">Specials</h3>");
                            console.log("success: " + response.content);
                            getSpecials();
                        }
                    })
                });
            });
        },
        error: function (xhr, err) {
            console.log("readyState: " + xhr.readyState + "\nstatus: " + xhr.status);
            console.log("responseText: " + xhr.responseText);
        }
    })
}