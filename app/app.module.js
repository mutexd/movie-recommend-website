'use strict';

angular.module('movieApp', [
	'ngRoute',
	'ngResource'
]);

//shared data between controller(user_id, access_token)
angular.
  module('movieApp').
    service('userService', function(){
      var self = this;
	  self.access_token = "non";
	  self.user_id = 0;
      self.setToken = function(token){
		self.access_token = token;
	  }
	  self.setUID = function(id){
		self.user_id = id;
	  }
	  self.getToken = function() {
		return self.access_token;
	  }
	  self.getUID = function() {
	    return self.user_id;
	  }
	});

angular.
  module('movieApp').
    directive('starCanvas', function(){
      function link(scope, element, attrs) {
		  var canvas = element[0];
		  loadStar(canvas, 'white', 5);
		  canvas.addEventListener('mousemove', function(evt) {
			var mousePos = getMousePos(canvas, evt);
			var numStar = Math.floor(mousePos.x/26) + 1;
			loadStar(canvas, "yellow", numStar);
			//console.log('Mouse position: ' + mousePos.x + ',' + mousePos.y + '--'+numStar);
		  }, false);
		  canvas.addEventListener('mouseout', function(evt) {
			loadStar(canvas, "white", 5);
		  }, false);
		  canvas.addEventListener('click', function(evt){
			var mousePos = getMousePos(canvas, evt);
			console.log('Click position: ' + mousePos.x + ',' + mousePos.y);
		  }, false);
	  }
      return {
		restrict: 'E',
		replace: true,
		scope: true,
		link: link,
		template: '<canvas id="myCanvas" width="130" height="30"></canvas>'
      };
    });

function loadStar(canvas, color, num) {
    var ctx = canvas.getContext('2d');
	ctx.save();
	for(var j=0;j<5;j++){
		if(j==0){
			ctx.translate(13,15);
		} else {
			ctx.translate(25,0);
		}
		ctx.beginPath();
		ctx.strokeStyle="orange";
		ctx.lineWidth="1";
		ctx.closePath();
		ctx.beginPath();
		for(var i=0;i<5;i++){
			ctx.lineTo(12*Math.cos((18+i*72)*Math.PI/180),-12*Math.sin((18+i*72)*Math.PI/180));
			ctx.lineTo(6*Math.cos((54+i*72)*Math.PI/180),-6*Math.sin((54+i*72)*Math.PI/180));
		}
		if (j<num) {
			ctx.fillStyle=color;
		} else {
			ctx.fillStyle="white";
		}
		ctx.fill();
		ctx.closePath();
		ctx.stroke();
	}
	ctx.restore();
};

function getMousePos(canvas, evt) {
	var rect = canvas.getBoundingClientRect();
	return {
		x: evt.clientX - rect.left,
		y: evt.clientY - rect.top
	};
}
