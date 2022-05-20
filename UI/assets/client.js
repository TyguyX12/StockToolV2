window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        //  cts, ts, & sts = "timestamp", used for executing on startup
        create_graph: function (cts, its, candles, indicators) {        
            return createGraph(cts, its, candles, indicators);
        },
        display_graph: function(ts, data) {
            return displayGraph(ts, data)
        },
        create_numpost_graph: function (ts, sentiment) {
            return createNumPostGraph(ts, sentiment);
        },
        display_numpost_graph: function (asset, data) {
            return displayNumPostGraph(asset, data);
        },
        create_totalsentiment_graph: function (ts, sentiment) {
            return createTotalSentimentGraph(ts, sentiment);
        },
        display_totalsentiment_graph: function (asset, ts, data) {
            return displayTotalSentimentGraph(asset, ts, data);
        },
        create_numpost_graph_db: function (ts, sentiment) {
            return createNumPostGraphDb(ts, sentiment);
        },
        display_numpost_graph_db: function (asset, data) {
            return displayNumPostGraphDb(asset, data);
        },
        create_totalsentiment_graph_db: function (ts, sentiment) {
            return createTotalSentimentGraphDb(ts, sentiment);
        },
        display_totalsentiment_graph_db: function (asset, ts, data) {
            return displayTotalSentimentGraphDb(asset, ts, data);
        },
    }
});


function createGraph(cts, its, candles, indicators) {
    if (!candles) {
        return []
    }
    candles.type = 'candlestick';
    if (!indicators.overlays & !indicators.figures) {               //  If no indicators, return the list of candles as data
        return [candles];
    } else {                                                        //  Otherwise, add the candles to the data and return it
        let data = [candles].concat(indicators.overlays);
        return data;
    }
        
};
function displayGraph(ts, data) {

    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();

    today = yyyy + '-' + mm + '-' + dd;
    console.log(today);

    return {
        data: data,
        layout:
        {
            title: 'Stock Price History',
            xaxis: { range: ["2022-02-01", today] }
        }
    }
}

function createNumPostGraph(ts, sentiment) {
    if (!sentiment) {
        return []
    }
    let dates = [], negatives = [], neutrals = [], positives = [], totals = [], zeroes = [], negativeScores = [], neutralScores = [], positiveScores = [], compoundScores = [];

    for (date in sentiment) {
        dates.push(date)
        sentimentScores = sentiment[date]
        negatives.push(sentimentScores[5])
        neutrals.push(sentimentScores[6])
        positives.push(sentimentScores[7])
        totals.push(parseInt(sentimentScores[5]) + parseInt(sentimentScores[6]) + parseInt(sentimentScores[7]))
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
function displayNumPostGraph(asset, data) {
    title = asset.slice(0, -3) + " Post Count History";
    let layout = { barmode: 'stack', title: title, hovermode: "x unified" };
    return { data: data, layout: layout };
}
function createTotalSentimentGraph(ts, sentiment) {
    if (!sentiment) {
        return []
    }
    let dates = [], negatives = [], neutrals = [], positives = [], totals = [], zeroes = [], negativeScores = [], neutralScores = [], positiveScores = [], compoundScores = [];

    for (date in sentiment) {
        dates.push(date)
        sentimentScores = sentiment[date]
        negativeScores.push(sentimentScores[0])
        neutralScores.push(sentimentScores[1])
        positiveScores.push(sentimentScores[2])
        compoundScores.push(sentimentScores[3])
        zeroes.push(0)
    }

    let compoundLine = {
        x: dates,
        y: compoundScores,
        name: 'Compound Scores',
        type: 'scatter',
    };
    let negativeScore = {
        x: dates,
        y: negativeScores,
        name: 'Negative Scores',
        type: 'scatter',
        showlegend: false,
        opacity: 0,
    };
    let neutralScore = {
        x: dates,
        y: neutralScores,
        name: 'Neutral Scores',
        type: 'scatter',
        showlegend: false,
        opacity: 0,
    };
    let positiveScore = {
        x: dates,
        y: positiveScores,
        name: 'Positive Scores',
        type: 'scatter',
        showlegend: false,
        opacity: 0,
    }
    let data = [positiveScore, neutralScore, negativeScore, compoundLine];

    return data;
}
function displayTotalSentimentGraph(asset, data) {
    title = asset.slice(0, -3) + " Sentiment History";
    let layout = { barmode: 'stack', title: title, hovermode: "x unified" };
    return { data: data, layout: layout };
}

function createNumPostGraphDb(ts, sentiment) {
    if (!sentiment) {
        return []
    }
    let dates = [], negatives = [], neutrals = [], positives = [], totals = [], zeroes = [], negativeScores = [], neutralScores = [], positiveScores = [], compoundScores = [];

    for (date in sentiment) {
        dates.push(date)
        sentimentScores = sentiment[date]
        negatives.push(sentimentScores[5])
        neutrals.push(sentimentScores[6])
        positives.push(sentimentScores[7])
        totals.push(parseInt(sentimentScores[5]) + parseInt(sentimentScores[6]) + parseInt(sentimentScores[7]))
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
   
    let data  = [negativeBar, neutralBar, positiveBar, hoverOver];

    return data;
}
function displayNumPostGraphDb(asset, data) {
    title = asset.slice(0, -3) + " Post Count History";
    let layout = { barmode: 'stack', title: title, hovermode: "x unified" };
    return { data: data, layout: layout };
}
function createTotalSentimentGraphDb(ts, sentiment) {
    if (!sentiment) {
        return []
    }
    let dates = [], negatives = [], neutrals = [], positives = [], totals = [], zeroes = [], negativeScores = [], neutralScores = [], positiveScores = [], compoundScores = [];

    for (date in sentiment) {
        dates.push(date)
        sentimentScores = sentiment[date]
        negativeScores.push(sentimentScores[0])
        neutralScores.push(sentimentScores[1])
        positiveScores.push(sentimentScores[2])
        compoundScores.push(sentimentScores[3])
        zeroes.push(0)
    }

    let compoundLine = {
        x: dates,
        y: compoundScores,
        name: 'Compound Scores',
        type: 'scatter',
    };
    let negativeScore = {
        x: dates,
        y: negativeScores,
        name: 'Negative Scores',
        type: 'scatter',
        showlegend: false,
        opacity: 0,
    };
    let neutralScore = {
        x: dates,
        y: neutralScores,
        name: 'Neutral Scores',
        type: 'scatter',
        showlegend: false,
        opacity: 0,
    };
    let positiveScore = {
        x: dates,
        y: positiveScores,
        name: 'Positive Scores',
        type: 'scatter',
        showlegend: false,
        opacity: 0,
    }
    let data = [positiveScore, neutralScore, negativeScore, compoundLine];

    return data;
}
function displayTotalSentimentGraphDb(asset, data) {
    title = asset.slice(0, -3) + " Sentiment History";
    let layout = { barmode: 'stack', title: title, hovermode: "x unified" };
    return { data: data, layout: layout };
}