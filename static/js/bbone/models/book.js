// site/js/bbone/models/book.js

var app = app || {};

app.Film = Backbone.Model.extend({
	defaults: {
		title: 'Not here',
		rating: 'Unknown',
		myrating: 'Not here',
		blurb: 'blurb',
		myblurb: 'myblurb'
		keywords: 'None'
	}
});
