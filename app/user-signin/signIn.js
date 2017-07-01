'use strict';

angular.module('userSignIn', []);

// service for sign up
angular.
  module('userSignIn').
    factory('signInSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/signin', {});
    }]);

angular.
  module('userSignIn').
    controller('signInController', ['signInSvc', '$location', function(signInSvc, $location){
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