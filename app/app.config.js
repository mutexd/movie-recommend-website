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

angular.
  module('movieApp').
    controller('movieController', function(){
      this.movieList = [{
        title:"Toy Story",
        year:1995,
        duration:81,
        thumb:"https://images-na.ssl-images-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@._V1_UX182_CR0,0,182,268_AL_.jpg",
        url:"http://www.imdb.com/title/tt0114709/?ref_=fn_tt_tt_1"
      }, {
        title:"Dead Man Walking",
        year:1995,
        duration:122,
        thumb: "https://images-na.ssl-images-amazon.com/images/M/MV5BMTM3NzA1MjM2N15BMl5BanBnXkFtZTcwMzY3MTMzNA@@._V1_UX182_CR0,0,182,268_AL_.jpg",
        url:"http://www.imdb.com/title/tt0112818/"
      }]; 
    });
