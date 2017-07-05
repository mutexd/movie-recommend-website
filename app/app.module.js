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

//drawing star
angular.
  module('movieApp').
  controller('starController', [function() {
	var self = this;
	var canvas = document.getElementById("star");
	self.loadStar = function(color, num){
		var cxt=canvas.getContext("2d");
		cxt.save();
		for(var j=0;j<5;j++){
			if(j==0){
				cxt.translate(13,15);
			} else {
				cxt.translate(25,0);
			}
			cxt.beginPath();
			cxt.strokeStyle="orange";
			cxt.lineWidth="1";
			cxt.closePath();
			cxt.beginPath();
			for(var i=0;i<5;i++){
				cxt.lineTo(12*Math.cos((18+i*72)*Math.PI/180),-12*Math.sin((18+i*72)*Math.PI/180));
				cxt.lineTo(6*Math.cos((54+i*72)*Math.PI/180),-6*Math.sin((54+i*72)*Math.PI/180));
			}
			if (j<num) {
				cxt.fillStyle=color;
			} else {
				cxt.fillStyle="white";
			}
			cxt.fill();
			cxt.closePath();
			cxt.stroke();
		}
		cxt.restore();
	};
	canvas.addEventListener('mousemove', function(evt) {
		var mousePos = getMousePos(canvas, evt);
		var numStar = Math.floor(mousePos.x/26) + 1;
		self.loadStar("yellow", numStar);
		console.log('Mouse position: ' + mousePos.x + ',' + mousePos.y + '--'+numStar);
	}, false);
	canvas.addEventListener('mouseout', function(evt) {
		self.loadStar("white", 5);
	}, false);
	canvas.addEventListener('click', function(evt){
		var mousePos = getMousePos(canvas, evt);
		console.log('Click position: ' + mousePos.x + ',' + mousePos.y);
	}, false);
	self.loadStar('white');
}]);

function getMousePos(canvas, evt) {
	var rect = canvas.getBoundingClientRect();
	return {
		x: evt.clientX - rect.left,
		y: evt.clientY - rect.top
	};
}
