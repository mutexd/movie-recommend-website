'use strict';
// service for recommendation
angular.
  module('movieApp').
    factory('recommendSvc', ['$resource', function($resource){
      return {
		api: function(token){
		  return $resource('http://localhost:5000/webmovie/api/v0.1/recommend/:userId?begin=:begin&end=:end',
			{userId:'@userId', begin:'@begin', end:'@end'},{
			  query: {
				method: 'GET',
				headers: {
				  'Authorization': 'Bearer ' + token
				}
			  }
			});
		}
      }
	}]);

// service for rated movies
angular.
  module('movieApp').
    factory('ratedSvc', ['$resource', function($resource){
      return {
		api: function(token){
		  return $resource('http://localhost:5000/webmovie/api/v0.1/rated/:userId?begin=:begin&end=:end',
			{userId:'@userId', begin:'@begin', end:'@end'},{
			  query: {
				method: 'GET',
				headers: {
				  'Authorization': 'Bearer ' + token
				}
			  }
			});
		}
      }
	}]);

// controller for user page
angular.
  module('movieApp').
    controller('userController', ['recommendSvc', 'ratedSvc', 'userService',
         function(recommendSvc, ratedSvc, userService){
      var self = this;
      var fields = {userId:userService.getUID(), begin:0, end:20};
      var token = userService.getToken();
      recommendSvc.api(token).query(fields,
		function(data){
		  if(data.status == "fail"){
			console.error(data);
		  } else {
			self.movieList = data;
		  }
		}, function(error){
		  console.error(error);
		}
	  );
      ratedSvc.api(token).query(fields,
		function(data){
		  if(data.status == "fail"){
			console.error(data);
		  } else {
			console.error(data);
		  }
		}, function(error){
		  console.error(error);
		}
	  );
	}]);

