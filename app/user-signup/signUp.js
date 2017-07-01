'use strict';

// service for sign up
angular.
  module('movieApp').
    factory('signUpSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/signup', {});
    }]);

angular.
  module('movieApp').
    controller('signUpController', ['signUpSvc', 'userService', '$location',
      function(signUpSvc, userService, $location){
      var self = this
      self.error_message = ""
      self.signUpRequest = function(fields) {
        if (fields.password != fields.confirm_pw) {
          self.error_message = "Entered passwords are not matched!"
        } else {
          // retrieve user_id, access_token,
          signUpSvc.save(fields, function(data){
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
          });
        }
      }
      self.onInput = function() {
        if (self.error_message != "") {
          self.error_message = ""
        }
      }
    }]);