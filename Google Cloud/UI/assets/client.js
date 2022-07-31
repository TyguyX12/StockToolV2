window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        //  cts, ts, & sts = "timestamp", used for executing on startup
        create_graph: function (cts, its, candles, indicators) {        
            return createGraph(candles, indicators);
        },
        display_graph: function(ts, ts2, data, asset, indicators) {
            return displayGraph(data, asset, indicators)
        },
        create_numpost_graph: function (ts, sentiment) {
            return createNumPostGraph(sentiment);
        },
        display_numpost_graph: function (ts, data, asset) {
            return displayNumPostGraph(data, asset);
        },
    }
});


function createGraph(candles, indicators) {

    if (!candles) {
        return []
    }
    candles.type = 'candlestick';
    if (indicators == undefined) {
        return [candles]
    }
    if (!indicators.overlays || indicators.overlays.length == 0) {               //  If no indicators, return the list of candles as data
        return [candles];
    } else {
        //  Otherwise, add the candles to the data and return it
        let data = [candles].concat(indicators.overlays);
        return data;
    }
        
};
function displayGraph(data, asset, indicators) {
    if (asset == undefined) {
        return {}
    }

    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();

    today = yyyy + '-' + mm + '-' + dd;
    var title = asset.slice(0, -3) + " Price History";
    try {
        if (!indicators || !indicators.figures || indicators.figures.length == 0) {
            let candlesChart = {
                data: data,
                layout: {
                    title: title,
                    xaxis: { range: ["2022-02-01", today] }
                }
            }
            return candlesChart
        }
        else {
            var counter = 1
            let traces = data;
            for (var i in indicators.figures) {
                counter = counter + 1
                let figure = indicators.figures[i]
                figure['xaxis'] = 'x' + counter;
                figure['yaxis'] = 'y' + counter;
                traces.push(figure)
            }

            var layout = {
                grid: { rows: counter, columns: 1, pattern: 'independent' },
                xaxis: {
                    rangeslider: {
                        visible: false
                    }
                }
            }
            let chart = {
                data: traces,
                layout: layout
            }
            return chart
        }
    } catch (error) {
        return {}
    }

}

function createNumPostGraph(sentiment) {
    if (!sentiment) {
        return undefined
    }
    let dates = [], negatives = [], neutrals = [], positives = [], totals = [], zeroes = [], negativeScores = [], neutralScores = [], positiveScores = [], compoundScores = [];

    for (date in sentiment) {
        dates.push(date)
        sentimentScores = sentiment[date]
        negatives.push(sentimentScores[4])
        neutrals.push(sentimentScores[5])
        positives.push(sentimentScores[6])
        totals.push(sentimentScores[7])
        zeroes.push(0)
    }

    let positiveBar = {
        x: dates,
        y: positives,
        name: 'Positives',
        type: 'bar',
        marker: {
            color: 'rgb(140,200,100)'
        }
    };

    let neutralBar = {
        x: dates,
        y: neutrals,
        name: 'Neutrals',
        type: 'bar',
        marker: {
            color: 'rgb(240,220,60)'
        }
    };

    let negativeBar = {
        x: dates,
        y: negatives,
        name: 'Negatives',
        type: 'bar',
        marker: {
            color: 'rgb(230,70,70)'
        }
    };
    let hoverOver = {
        x: dates,
        y: totals,
        base: zeroes,
        type: "bar",
        name: "Total Posts",
        showlegend: false,
        opacity: 0,
    };

    let data = [negativeBar, neutralBar, positiveBar, hoverOver];

    return data;
}
function displayNumPostGraph(data, asset) {
    if (asset == undefined) {
        return {}
    }
    if (data == undefined) {
        title = "No Sentiment Data For " + asset.slice(0, -3);
        let layout = { title: title };

        return { data: data, layout: layout }
    }
    title = asset.slice(0, -3) + " Post Count History";
    let layout = { barmode: 'stack', title: title, hovermode: "x unified" };

    return { data: data, layout: layout };
}
