$(document).ready(function(){

    $(".btn").click(function(){


        $(".btn").removeClass("active");//removes classes everywhere
        $(this).toggleClass("active");//adds the class at the right button

        // Get value from input element on the page
        var choiceValue = $(this).attr("id");
        var periodValue = $("#period").find("a.active").attr("data-filter");

        $('.grid').load('/collection' +  ' .grid', {choice: choiceValue, period:periodValue}, function(){
            $('.grid').imagesLoaded(function () {
                $('.grid').masonry({
                    itemSelector: '.grid-item', // use a separate class for itemSelector, other than .col-
                    percentPosition: true
                });
            });
        });
    });

    $("#period").find('a').click(function() {
        var $period = $("#period");
        $period.find("a").removeClass("active");
        $(this).addClass("active");

        var choiceValue = $("#nav-button").find("button.active").attr("id");
        var periodValue = $(this).attr("data-filter");

        $('.grid').load('/collection' +  ' .grid', {choice: choiceValue, period:periodValue}, function(){
            $('.grid').imagesLoaded(function () {
                $('.grid').masonry({
                    itemSelector: '.grid-item', // use a separate class for itemSelector, other than .col-
                    percentPosition: true
                });
            });
        });
    });


    $('.grid').imagesLoaded(function () {
        $('.grid').masonry({
            itemSelector: '.grid-item', // use a separate class for itemSelector, other than .col-
            percentPosition: true
        });
    });


});
