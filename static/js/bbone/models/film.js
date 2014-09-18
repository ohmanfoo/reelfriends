// site/js/bbone/models/film.js

var app = app || {};

app.Film = Backbone.Model.extend({
	defaults: {
		title: 'Not here',
		rating: 'Unknown',
		blurb: 'blurb',
		keywords: 'None'
	}
});
