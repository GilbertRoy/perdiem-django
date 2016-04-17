$(document).ready(function() {
    'use strict'

    // CSRF
    var csrftoken = $.cookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Invest num shares input buttons
    function get_num_shares() {
        var value = $('.invest-num-shares > input').val();
        if (!$.isNumeric(value)) value = 1;
        return parseInt(value);
    }
    function num_shares_updated() {
        // Enforce minimum of one
        var num_shares = Math.max(1, get_num_shares());
        $('.invest-num-shares > input').val(num_shares);

        // Disable minus button when only 1 share
        if (num_shares === 1) {
            $('.invest-num-shares > button#remove-shares').addClass('disabled').prop('disabled', true);
        } else {
            $('.invest-num-shares > button#remove-shares').removeClass('disabled').prop('disabled', false);
        }

        // Update invest button text
        var button_text = "Buy " + num_shares + " Share";
        if (num_shares !== 1) button_text += "s";
        var amount = get_total_cost_cents() / 100;
        button_text += " ($" + amount + ")*";
        $('button#invest-button').text(button_text);
    }
    $('.invest-num-shares > input').change(function() {
        num_shares_updated();
    });
    num_shares_updated();

    // Press buttons to update shares
    $('.invest-num-shares > button').click(function() {
        // Get the current number of shares
        var num_shares = get_num_shares();

        // Decrement or increment number of shares based on button pressed
        if ($(this).is('.invest-num-shares > button#remove-shares')) {
            num_shares = Math.max(1, num_shares - 1);
        } else if ($(this).is('.invest-num-shares > button#add-shares')) {
            num_shares += 1;
        } else {
            console.log("Unexpected invest-num-shares button pressed.");
        }

        // Set num shares in input
        $('.invest-num-shares > input').val(num_shares);
        num_shares_updated();
    });

    // Cost for shares
    function get_total_cost_cents() {
        var subtotal = get_num_shares() * share_value_cents;
        var perdiem_fee_cents = perdiem_fee * 100;
        var total = (perdiem_fee_cents + subtotal) * 1.029 + 30; // Stripe 2.9% + $0.30 fee
        return Math.ceil(total);
    }

    // Click Invest button
    $('#invest-button').click(function(e) {
        stripe_handler.open({
            name: 'PerDiem',
            description: 'Invest in ' + artist_name,
            amount: get_total_cost_cents()
        });
        e.preventDefault();
    });

    $(window).on('popstate', function() {
        handler.close();
    });
});
