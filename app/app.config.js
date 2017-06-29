'use strict';

angular.
  module('movieApp').
    config(['$routeProvider', '$locationProvider', 
      function config($routeProvider, $locationProvider) {
      $locationProvider.hashPrefix('!');
      
      $routeProvider
        .when('/', {
          templateUrl: "movie-list-ranked/rankedMovieList.html",
          controller: "movieController"
        })
        .when('/login', {
          templateUrl: "user-signin/signIn.html",
          controller: "signInController"
        })
        .when('/logon', {
          templateUrl: "user-signup/signUp.html",
          controller: "signUpController"
        })
        .when('/:userId', {
          templateUrl: "user-page/recommend.html",
          controller: "userController"
        })
        .otherwise({ redirectTo: '/' });
    }]
  );
