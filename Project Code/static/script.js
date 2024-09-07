$(document).ready(function() {
    // Function to set image source
    function setImageSrc(plotId, url) {
        $.get(url, function(data) {
            $(plotId).attr('src', data).show();
        }).fail(function(xhr) {
            $('#error-message').text('Error: ' + xhr.responseJSON.error);
        });
    }

    // Load Average Monthly Plot
    setImageSrc('#avg-monthly-plot', '/plot_avg_monthly');

    // Load Seasonal Decompose Plot
    setImageSrc('#seasonal-decompose-plot', '/plot_seasonal_decompose');

    // Load Major Events Plot
    setImageSrc('#major-events-plot', '/plot_major_events');

    // Handle Regional Form Submission
    $('#regional-analysis-form').on('submit', function(e) {
        e.preventDefault();
        $.post('/plot_regional', $(this).serialize(), function(data) {
            $('#regional-plot').attr('src', data.plot_file).show();
        }).fail(function(xhr) {
            $('#error-message').text('Error: ' + xhr.responseJSON.error);
        });
    });

    // Handle Product Trend Form Submission
    $('#product-trend-form').on('submit', function(e) {
        e.preventDefault();
        $.post('/plot_product_trend', $(this).serialize(), function(data) {
            $('#product-trend-plot').attr('src', data.plot_file).show();
        }).fail(function(xhr) {
            $('#error-message').text('Error: ' + xhr.responseJSON.error);
        });
    });

    // Handle Price Forecast Form Submission
    $('#price-forecast-form').on('submit', function(e) {
        e.preventDefault();
        $.post('/plot_price_forecast', $(this).serialize(), function(data) {
            $('#forecast-plot').attr('src', data.plot_file).show();
        }).fail(function(xhr) {
            $('#error-message').text('Error: ' + xhr.responseJSON.error);
        });
    });

    // Handle Search Product Form Submission (First Search Bar)
    $('#search-product-form').on('submit', function(event) {
        event.preventDefault();
        $.post('/search_product', $(this).serialize(), function(response) {
            $('#search-results tbody').empty();
            if (response.results.length === 0) {
                $('#search-results').hide();
            } else {
                response.results.forEach(function(item) {
                    $('#search-results tbody').append(
                        '<tr><td>' + item.Name + '</td><td>' + item.Price + '</td><td>' + item.Store + '</td></tr>'
                    );
                });
                $('#search-results').show();
            }
        }).fail(function(xhr) {
            $('#error-message').text('Error: ' + xhr.responseJSON.error);
        });
    });

});
