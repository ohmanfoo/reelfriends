// site/js/bbone/views/library.js

var app = app || {};

app.MyLibraryView = Backbone.View.extend({

		el: '#myfilms',

		events:{
			'click #add':'addFilm'
		},

		initialize: function() {
			this.collection = new app.MyLibrary();
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

			var myfilmView = new app.MyFilmView({
				model: item
			});

			this.$el.append( myfilmView.render().el );

		},

		addFilm: function( e ) {
			e.preventDefault();
			var formData = {};

			$('#addFilm div').children('input').each( function(i, el) {
				if( $(el).val() != '') {
					formData[el.id] = $( el ).val();
				}
			});

			this.collection.create( formData )
		}
	
});
