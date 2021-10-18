from dash_extensions.enrich import DashProxy
import dash_extensions.enrich as plugins

app = DashProxy(__name__, suppress_callback_exceptions=True, external_scripts=['homepage.js'],    transforms=[
    plugins.ServersideOutputTransform(),
    plugins.MultiplexerTransform(),
    plugins.TriggerTransform(),
    plugins.NoOutputTransform(),
])
server = app.server
