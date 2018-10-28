// custom script for quantumscientific web application

document.addEventListener("DOMContentLoaded", function(){

	//code
	$('.preloader-background').delay(600).fadeOut(600);
	//$('.preloader-wrapper').delay(250).fadeOut(500);
	$('.spinner').delay(600).fadeOut(1000);

	$('.header_links').delay(700).addClass('animated fadeInLeftBig slow')
	$('.admin_links').delay(700).addClass('animated fadeInLeftBig slow')
	$('.contentwrap').delay(700).addClass('animated fadeInRightBig slow')

});// end: addEventListener [ DOMContentLoaded ]

$(function() {

	//code
	$('.carousel.carousel-slider').carousel({
		fullWidth: true,
		indicators: true,
	});

	$('.collapsible').collapsible();

	$('.fixed-action-btn').floatingActionButton();

	$('select').formSelect();

	$('.carousel.carousel-slider').carousel({
		fullWidth: true,
		indicators: true,
	});

});// end: MAIN FUNCTION WRAP