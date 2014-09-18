// site/js/bbone/collections/library.js

var app = app || {};

app.Library = Backbone.Collection.extend({
	model: app.Film,
	url: '/api/films.json'
});
