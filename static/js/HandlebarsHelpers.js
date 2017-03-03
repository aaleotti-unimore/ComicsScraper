Handlebars.registerHelper("formatDate", function (datetime, format) {
    if (moment && datetime) {
        // can use other formats like 'lll' too
        format = "DD/MM/YYYY" || format;
        return moment(datetime).format(format);
    }
    else {
        return "";
    }
});

Handlebars.registerHelper("hypenate", function (str) {
    if (str && typeof str === 'string') {
        return str.replace(/[^\w\s]/gi, '').split(' ').join('-');
    }
});