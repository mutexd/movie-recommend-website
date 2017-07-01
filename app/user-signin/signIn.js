'use strict';

// service for sign in
angular.
  module('movieApp').
    factory('signInSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/signin', {});
    }]);

angular.
  module('movieApp').
    controller('signInController', ['signInSvc', 'userService', '$location',
      function(signInSvc, userService, $location){
      var self = this
      self.error_message = ""
      self.signInRequest = function(fields) {
          // retrieve user_id, access_token,
          signInSvc.save(fields,
            function(data){
              if (data.status == "fail") {
                self.error_message = data.error
              } else {
                self.auth = data
                userService.setUID(data.user_id)
                userService.setToken(data.access_token)
                // redirect to user page
                $location.url('/'+self.auth.user_id)
              }
            }, function(error){
              console.error(error)
            }
          );
      }
      self.onInput = function() {
        if (self.error_message != "") {
          self.error_message = ""
        }
      }
    }]);