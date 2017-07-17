'use strict';

// service for getting average ranked movie list
angular.
  module('movieApp').
    factory('rankedListSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/guest?begin=:begin&end=:end',
		{begin:'@begin', end:'@end'}, {
			query: {
				method: 'GET'
		    }
		});
    }]);

angular.
  module('movieApp').
    controller('movieController', ['rankedListSvc', function(rankedListSvc){
	  var self = this;
	  var fields = {begin:0, end:20};
	  rankedListSvc.query(fields, function(data){
		if (data.status == "fail"){
		  console.error(data)
		} else {
		  self.movieList = data.movie_list
		}
	  }, function(error){
		console.error(error)
	  });
    }]);