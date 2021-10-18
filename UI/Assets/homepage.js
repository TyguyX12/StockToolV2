window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        create_indicator_forms: function (ts, forms) {
            return createIndicatorForms(forms);
        },
        create_indicator_figures: function (ts, traces) {
            return createIndicatorFigures(ts, traces);
        },
        create_graph: function (cts, its, candles, indicators) {
            return createGraph(cts, its, candles, indicators);
        },
        display_graph: function(ts, data) {
            return displayGraph(ts, data)
        }
    }
});


function createIndicatorForms(ts, forms) {
    console.log(forms)
    if (forms == undefined) {
        return {};
    }

    var children = [];
    var value;
    
    var dcc = (type, properties) => {
        return { props: properties, type: type, namespace: 'dash_core_components' }
    };

    var html = (type, children) => {
        return { props: {children: children}, type: type, namespace: 'dash_html_components'}
    };

    for (let indidicator in forms) {
        if (value == undefined) {
            value = indicator
        }; 

        var form = [];
        for (let option in indicator.options) {
            form.push(html('P', option));
        }
        let properties = {
            label: indicator.full_name,
            value: indicator,
            children: form
        };

        let tab = dcc('Tab', properties);
        children.push(tab);
    };
    return children, value
};


function createIndicatorFigures(ts, traces) {
    var children = []
    if (!traces) {
        return {}
    } else {
        var dcc = (type, properties) => {
            return { props: properties, type: type, namespace: 'dash_core_components' }
        }
        for (let trace in traces) {
            let graph = [dcc('Graph', {figure: trace})]
            children.concat(graph)
        }
        return children
    }
}


function createGraph(cts, its, candles, indicators) {
    if (!candles) {
        return []
    } 
    candles.type = 'candlestick';
    if (!indicators.overlays & !indicators.figures) {
        return [candles];
    } else {
        let data = [candles].concat(indicators.overlays);
        return data;
    }
        
};

function displayGraph(ts, data) {
    return {data: data, layout: {title: ''}}
}

