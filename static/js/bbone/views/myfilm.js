// site/js/bbone/views/myfilm.js

var app = app || {};

app.MyFilmView = Backbone.View.extend({
	tagName: 'div',
	className: 'filmContainer post flex-content',
	template: _.template( $('#myFilmTemplate').html() ),
	events: {
		'click .delete': 'deleteFilm'
	},

	deleteFilm: function () {
		// delete model...
		this.model.destroy();
		// delete view...
		this.remove();
	},

	render: function() {

		this.$el.html( this.template( this.model.toJSON() ));

		return this;
	}
	
});
