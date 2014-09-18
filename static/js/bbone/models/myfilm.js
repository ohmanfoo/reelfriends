// site/js/bbone/models/myfilm.js

var app = app || {};

app.MyFilm = Backbone.Model.extend({
	defaults: {
		mytitle: 'Not here',
		myrating: 'Unknown',
		myblurb: 'blurb',
		user: 'username',
		mykeywords: 'None'
	}
});
