'use strict';

angular.module('userSignUp', []);

// service for sign up
angular.
  module('userSignUp').
    factory('signUpSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/signup', {});
    }]);

angular.
  module('userSignUp').
    controller('signUpController', ['signUpSvc', '$location', function(signUpSvc, $location){
      var self = this
      self.error_message = ""
      self.signUpRequest = function(fields) {
        if (fields.password != fields.confirm_pw) {
          self.error_message = "Password is not matched!"
        } else {
          // retrieve user_id, access_token,
          self.auth = signUpSvc.save(fields);
          // redirect to user page
          $location.url('/:self.auth.user_id')
        }
      }
      self.onInput = function() {
        if (self.error_message != "") {
          self.error_message = ""
        }
      }
    }]);