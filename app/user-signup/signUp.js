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
    controller('signUpController', ['signUpSvc', function(signUpSvc){
      var self = this
      self.error_message = ""
      self.signUpRequest = function(fields) {
        if (fields.password != fields.confirm_pw) {
          self.error_message = "Password is not matched!"
        } else {
          signUpSvc.save(fields);
        }
      }
      self.onInput = function() {
        if (self.error_message != "") {
          self.error_message = ""
        }
      }
    }]);