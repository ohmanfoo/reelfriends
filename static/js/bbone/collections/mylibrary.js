// site/js/bbone/collections/mylibrary.js

var app = app || {};

app.MyLibrary = Backbone.Collection.extend({
	model: app.MyFilm,
	url: '/api/myfilms.json'
});
