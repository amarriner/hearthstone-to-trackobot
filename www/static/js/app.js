(function() {
    'use strict';

    //
    // Call API to save values
    //
    function doSave() {
        $.ajax({
            url: '/hs-parse/api/set',
            data: 't=' + $('#token').val() + '&mode=' + $('#mode-select').val() + '&rank=' + $('#rank-select').val()
        }).done(function(data) {
            $('#save-message').stop().animate({opacity:'100'}).text(data.message).css('display', 'block').fadeOut(3000);
        }).fail(function(data) {
            $('#save-message').stop().animate({opacity:'100'}).text(data.responseJSON.message).css('display', 'block').fadeOut(3000);
        });
    }

    $(document).ready(function() {

        //
        // Set focus for token field
        //
        $('#token').focus();

        //
        // Bind ENTER to token field
        //
        $('#token').keypress(function(event) {
            if (event.which == 13) {
               doSave();
            }
        });

        //
        // Get current mode
        //
        $.ajax({
           url: '/hs-parse/api/get-mode',
        }).done(function(data) {
           $('#mode-select').val(data.mode).prop('disabled', false);
        });

        //
        // Get current rank
        //
        $.ajax({
           url: '/hs-parse/api/get-rank',
        }).done(function(data) {
           $('#rank-select').val(data.rank).prop('disabled', false);
        });

        //
        // Save selection
        //
        $('#save-button').click(function() {
           doSave();
        });

    });

} ());
