(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['card'] = template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "        <a href=\"/show_issues/"
    + alias4(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data}) : helper)))
    + "\">\n            <img class=\"card-img-top img-fluid\" src=\""
    + alias4(((helper = (helper = helpers.image || (depth0 != null ? depth0.image : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"image","hash":{},"data":data}) : helper)))
    + "\">\n        </a>\n        <div class=\"card-block\">\n            <h6 class=\"card-title\">"
    + alias4(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data}) : helper)))
    + "</h6>\n            <h6 class=\"card-subtitle mb-2 text-muted\">"
    + alias4(((helper = (helper = helpers.subtitle || (depth0 != null ? depth0.subtitle : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"subtitle","hash":{},"data":data}) : helper)))
    + "</h6>\n            <h6 class=\"card-text text-muted\">"
    + alias4(((helper = (helper = helpers.reprint || (depth0 != null ? depth0.reprint : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"reprint","hash":{},"data":data}) : helper)))
    + "</h6>\n            <h7 class=\"card-text text-muted\">"
    + alias4(container.lambda(((stack1 = (depth0 != null ? depth0.serie : depth0)) != null ? stack1.id : stack1), depth0))
    + "</h7>\n            <h6 class=\"card-text text-muted\">"
    + alias4(((helper = (helper = helpers.price || (depth0 != null ? depth0.price : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"price","hash":{},"data":data}) : helper)))
    + "</h6>\n        </div>\n        <ul class=\"list-group list-group-flush text-center\">\n            <li class=\"list-group-item\">\n                <div class=\"mx-auto\">\n                    <form>\n                        <button id=\"btn-sum-"
    + alias4(((helper = (helper = helpers.index || (depth0 != null ? depth0.index : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"index","hash":{},"data":data}) : helper)))
    + "\" class=\"btn btn-sm btn-outline-primary\" type=\"button\">\n                            <i class=\"fa fa-list\" aria-hidden=\"true\"></i>\n                        </button>\n                        <a class=\"btn btn-sm btn-outline-primary\" href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\" role=\"button\"> <i\n                                class=\"fa fa-shopping-cart\" aria-hidden=\"true\"></i></a>\n"
    + ((stack1 = helpers.unless.call(alias1,(depth0 != null ? depth0.specials : depth0),{"name":"unless","hash":{},"fn":container.program(2, data, 0),"inverse":container.program(4, data, 0),"data":data})) != null ? stack1 : "")
    + "                    </form>\n                </div>\n            </li>\n        </ul>\n        <div class=\"card-footer\">\n            <small>\n                "
    + alias4((helpers.formatDate || (depth0 && depth0.formatDate) || alias2).call(alias1,(depth0 != null ? depth0.date : depth0),{"name":"formatDate","hash":{},"data":data}))
    + "\n            </small>\n        </div>\n";
},"2":function(container,depth0,helpers,partials,data) {
    var helper;

  return "                            <span></span>\n                            <button id=\"btn-add-"
    + container.escapeExpression(((helper = (helper = helpers.index || (depth0 != null ? depth0.index : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : {},{"name":"index","hash":{},"data":data}) : helper)))
    + "\" class=\"btn btn-sm btn-outline-success\" type=\"button\">\n                                <i class=\"fa fa-plus\" aria-hidden=\"true\"></i>\n                            </button>\n";
},"4":function(container,depth0,helpers,partials,data) {
    var helper;

  return "                            <span></span>\n                            <button id=\"btn-del-"
    + container.escapeExpression(((helper = (helper = helpers.index || (depth0 != null ? depth0.index : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : {},{"name":"index","hash":{},"data":data}) : helper)))
    + "\" class=\"btn btn-sm btn-outline-danger\" type=\"button\">\n                                <i class=\"fa fa-times\" aria-hidden=\"true\"></i>\n                            </button>\n";
},"6":function(container,depth0,helpers,partials,data) {
    return "                        <li class=\"list-group-item\">"
    + container.escapeExpression(container.lambda(depth0, depth0))
    + "</li>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"card\">\n"
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.title : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "</div>\n<!-- Modal -->\n<div class=\"modal fade\" id=\"mod-"
    + alias4(((helper = (helper = helpers.index || (depth0 != null ? depth0.index : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"index","hash":{},"data":data}) : helper)))
    + "\" role=\"dialog\">\n    <div class=\"modal-dialog modal-sm modal-lg\">\n\n        <!-- Modal content-->\n        <div class=\"modal-content\">\n            <div class=\"modal-header\">\n                <button type=\"button\" class=\"close\" data-dismiss=\"modal\">&times;</button>\n                <h6 class=\"modal-title\">Sommario "
    + alias4(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data}) : helper)))
    + "</h6>\n            </div>\n            <div class=\"modal-body\">\n                <ul class=\"list-group list-group-flush\">\n"
    + ((stack1 = helpers.each.call(alias1,(depth0 != null ? depth0.summary : depth0),{"name":"each","hash":{},"fn":container.program(6, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "                </ul>\n            </div>\n            <div class=\"modal-footer\">\n                <button type=\"button\" class=\"btn btn-small btn-default\" data-dismiss=\"modal\">Close\n                </button>\n            </div>\n        </div>\n\n    </div>\n</div>\n<!-- END Modal -->";
},"useData":true});
})();