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
          controller: "movieController"
        })
        .when('/logon', {
          templateUrl: "user-signup/signUp.html",
          controller: "movieController"
        })
        .when('/:userId', {
          templateUrl: "userMainPage.html",
          controller: "userController"
        })
        .otherwise({ redirectTo: '/' });
    }]
  );
