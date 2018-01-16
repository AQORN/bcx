
<html>
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
?>

<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
<script src="http://code.highcharts.com/highcharts.js" type="text/javascript"></script>
<script src="http://code.highcharts.com/modules/stock.js" type="text/javascript"></script>
<script src="http://code.highcharts.com/modules/map.js" type="text/javascript"></script>
<script type="text/javascript">
$.getJSON('https://www.highcharts.com/samples/data/jsonp.php?filename=aapl-c.json&callback=?', function (data) {
    // Create the chart
    Highcharts.stockChart('container', {
        rangeSelector: {
            selected: 1
        },
        title: {
            text: 'AAPL Stock Price'
        },
        series: [{
            name: 'AAPL',
            data: data,
            tooltip: {
                valueDecimals: 2
            }
        }]
    });
});
</script>
</head>

<body>
<div id="container" style="width:75%; height:400px;"></div>

<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

require ('_api_.php');

$response = CallAPI('GET', 'http://localhost:5000/bcx-web/api/v1.0/tasks');
echo "<pre>" . $response . "</pre>";

?>
</body>
</html>