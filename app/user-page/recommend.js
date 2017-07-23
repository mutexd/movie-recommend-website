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

// service for rated movies
angular.
  module('movieApp').
    factory('addRateSvc', ['$resource', function($resource){
      return {
		api: function(token){
		  return $resource('http://localhost:5000/webmovie/api/v0.1/add_rating/:userId',
			{userId:'@userId'},{
			  save: {
				method: 'POST',
				headers: {
				  'Authorization': 'Bearer ' + token
				}
			  }
			});
		}
	  }
	}]);

// star UI displayed in recommendation page
angular.
  module('movieApp').
    directive('starCanvas', function(){
      function link(scope, element, attrs, ngCtrl) {
		  var canvas = element[0];
		  loadStar(canvas, 'white', 5);
		  canvas.addEventListener('mousemove', function(evt) {
			var mousePos = getMousePos(canvas, evt);
			var numStar = Math.floor(mousePos.x/26) + 1;
			loadStar(canvas, "yellow", numStar);
			//console.log('Mouse position: ' + mousePos.x + ',' + mousePos.y + '--'+numStar);
		  }, false);
		  canvas.addEventListener('mouseout', function(evt) {
			loadStar(canvas, "white", 5);
		  }, false);
		  canvas.addEventListener('click', function(evt){
			var mousePos = getMousePos(canvas, evt);
			var numStar = Math.floor(mousePos.x/26) + 1;
			ngCtrl.setRate(attrs.index, numStar);
		  }, false);
	  }
      return {
		restrict: 'E',
		replace: true,
		require: "^ngController",
		scope: {
			title: '@',
			index: '@'
		},
		link: link,
		template: '<canvas id="canvas{{title}}" width="130" height="30"></canvas>'
      };
    });

// controller for user page
angular.
  module('movieApp').
    controller('userController', ['recommendSvc', 'ratedSvc', 'addRateSvc', 'userService',
         function(recommendSvc, ratedSvc, addRateSvc, userService){
      var self = this;
      var fields = {userId:userService.getUID(), begin:0, end:20};
      var token = userService.getToken();
      recommendSvc.api(token).query(fields,
		function(data){
		  if(data.status == "fail"){
			console.error(data);
		  } else {
			self.movieList = data.movie_list;
			console.log(data)
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
			self.ratedList = data.movie_list;
			console.log(data);
		  }
		}, function(error){
		  console.error(error);
		}
	  );
	  self.logout = function(){
		userService.setToken("");
		userService.setUID(0);
	  };
	  self.setRate = function(index, numStar) {
		console.log('idx:' + index + " star:" + numStar);
		fields.movie_id = self.movieList[index].movie_id;
		fields.rating = numStar;
		addRateSvc.api(token).save(fields,
			function(data){
				console.log(data);
			}, function(error){
				console.error(error);
			}
		);
		//return self.movieList[index] = numStar;
	  };
	}]);

