'use strict';

angular.module('movieApp', [
	'ngRoute',
	'ngResource'
]);

//shared data between controller(user_id, access_token)
angular.
  module('movieApp').
    service('userService', function(){
      var self = this;
	  self.access_token = "non";
	  self.user_id = 0;
      self.setToken = function(token){
		self.access_token = token;
	  }
	  self.setUID = function(id){
		self.user_id = id;
	  }
	  self.getToken = function() {
		return self.access_token;
	  }
	  self.getUID = function() {
	    return self.user_id;
	  }
	});