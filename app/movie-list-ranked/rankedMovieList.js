'use strict';

angular.module('rankedMovieList', []);

angular.
  module('rankedMovieList').
    factory('rankedListSvc', ['$resource', function($resource){
      return $resource('http://localhost:8080/movielist/ranked', {});
    }]);

angular.
  module('rankedMovieList').
    controller('movieController', ['rankedListSvc', function(rankedListSvc){
      var self = this
      self.movieList = rankedListSvc.query();
    }]);

