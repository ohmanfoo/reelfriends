// site/js/bbone/views/film.js

var app = app || {};

app.FilmView = Backbone.View.extend({
		tagName: 'div',
		className: 'filmContainer post flex-content',
		template: _.template( $('#filmTemplate').html() ),
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
