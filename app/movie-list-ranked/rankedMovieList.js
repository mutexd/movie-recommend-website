'use strict';

angular.module('rankedMovieList', []);

angular.
  module('rankedMovieList').
    factory('rankedListSvc', ['$resource', function($resource){
      return $resource('http://localhost:5000/webmovie/api/v0.1/guest?begin=0&end=20', {});
    }]);

angular.
  module('rankedMovieList').
    controller('movieController', ['rankedListSvc', function(rankedListSvc){
      var self = this
      self.movieList = rankedListSvc.query();
    }]);

