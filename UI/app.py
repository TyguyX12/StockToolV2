from dash_extensions.enrich import DashProxy
import dash_extensions.enrich as plugins

app = DashProxy(__name__, suppress_callback_exceptions=True, external_scripts=['assets/client.js'], external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"], transforms=[
    plugins.ServersideOutputTransform(),            # enable use of ServersideOutput objects
    plugins.MultiplexerTransform(),                 # makes it possible to target an output multiple times in callbacks
    plugins.TriggerTransform(),                     # enable use of Trigger objects 
    plugins.NoOutputTransform(),                    # enable callbacks without output
])
server = app.server
