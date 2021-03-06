"""
A sample Hello World server.
"""
import os

from twitterService import twitterstream

from multiprocessing import Process


from flask import Flask, render_template

# pylint: disable=C0103
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"
    
    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')
    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

def start_flask():
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')

if __name__ == '__main__':
    p = Process(target=start_flask)
    p.start()
    twitterstream.start_live_listener()

