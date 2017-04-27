'use strict';

angular.module('rankedMovieList', ['ngResource']);

angular.
  module('rankedMovieList').
    factory('rankedListSvc', ['$resource', function($resource){
      return $resource('movie-list-ranked/movies.json', {});
    }]);

angular.
  module('rankedMovieList').
    controller('movieController', ['rankedListSvc', function(rankedListSvc){
      var self = this
      self.movieList = rankedListSvc.query();
    }]);

