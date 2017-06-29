'use strict';

angular.module('recommend', []);

// service for recommendation
angular.
  module('recommend').
    factory('recommendSvc', ['$resource', function($resource){
	  return $resource('http://localhost/5000/webmovie/api/v0.1/recommend/:userId', {});
	}]);

// service for rated movies
angular.
  module('recommend').
    factory('ratedSvc', ['$resource', function($resource){
	  return $resource('http://localhost/5000/webmovie/api/v0.1/rated/:userId', {});
	}]);

// testing 
angular.
  module('recommend').
    factory('rankedSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/guest?begin=0&end=20', {});
    }]);

// controller for user page
angular.
  module('recommend').
    controller('userController', ['recommendSvc', 'ratedSvc', 'rankedSvc', 
    	function(recommendSvc, ratedSvc, rankedSvc){
    	var self = this
    	self.recommendRequest = recommendSvc.save()
    	self.ratedRequest = ratedSvc.save()
    	self.movieList = rankedSvc.query()
	}]);

