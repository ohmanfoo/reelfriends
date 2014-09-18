// site/js/bbone/views/book.js

var app = app || {};

app.FilmView = Backbone.View.extend({
		tagName: 'div',
		className: 'filmContainer',
		template: _.template( $('filmTemplate').html() ),

		render: function() {

			this.$el.html( this.template( this.model.toJSON() ));

			return this;
		}
	
});
