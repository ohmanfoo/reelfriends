// site/js/bbone/views/library.js

var app = app || {};

app.LibraryView = Backbone.View.extend({

		el: '#films',

		events:{
			'click #add':'addFilm'
		},

		initialize: function() {
			this.collection = new app.Library();
			this.collection.fetch({reset: true});
			this.render();

			this.listenTo( this.collection, 'add', this.renderFilm);
			this.listenTo( this.collection, 'reset', this.render );

		},

		render: function () {
			this.collection.each(function( item ) {
				this.renderFilm( item );
			}, this );
			// body...
		},

		renderFilm: function( item ) {

			var filmView = new app.FilmView({
				model: item
			});

			this.$el.append( filmView.render().el );

		},

		addFilm: function( e ) {
			e.preventDefault();
			var formData = {};

			$('#addFilm div').children('input').each( function(i, el) {
				if( $(el).val() != '') {
					formData[el.id] = $( el ).val();
				}
			});

			this.collection.add( new app.Film( formData ))
		}
	
});
