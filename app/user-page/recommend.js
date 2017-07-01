'use strict';
// service for recommendation
angular.
  module('movieApp').
    factory('recommendSvc', ['$resource', function($resource){
	  return $resource('http://localhost:5000/webmovie/api/v0.1/recommend/:userId', {userId:'@userId'});
	}]);

// service for rated movies
angular.
  module('movieApp').
    factory('ratedSvc', ['$resource', function($resource){
	  return $resource('http://localhost:5000/webmovie/api/v0.1/rated/:userId', {userId:'@userId'});
	}]);

// testing 
angular.
  module('movieApp').
    factory('rankedSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/guest?begin=0&end=20', {});
    }]);

// controller for user page
angular.
  module('movieApp').
    controller('userController', ['recommendSvc', 'ratedSvc', 'rankedSvc', 'userService',
         function(recommendSvc, ratedSvc, rankedSvc, userService){
      var self = this
      var fields = {userId:userService.getUID()}
      console.error(userService.getToken())
      self.recommendRequest = recommendSvc.save(fields)
      self.ratedRequest = ratedSvc.save(fields)
      self.movieList = rankedSvc.query()
	}]);

