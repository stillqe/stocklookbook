$(document).ready(function(){
    $(document).on('click','.radio', function() {
        var period = $(this).attr('value');
        $(this).hide();
        req = $.ajax({
            url: '/update/'
            type: 'GET',
            data: {period: period}
        });

        req.done(function(data) {
            $('#display').fadeOut(100).fadeIn(100);
            $('#display').html(data);
        });
    });
});