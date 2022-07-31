from APIs import alpha_vantage_tt
from APIs import yahoo_finance_tt
import os
import json
import pathlib

## make sure to create and populate the .env file

### This automatically loads the api_info.json file which specifies the environment variables for the API, the types its supports. It does not load them in, just their names. Passes the specific key or oauth info into a trading tool API function.

class Librarian:

    def __init__(self, path, api_name):
        self.supported = None
        with open(path.joinpath('api_info.json').resolve(), 'r') as info:
            raw = info.read()
            self.supported = json.loads(raw)
        self._api_name = api_name if api_name in self.supported.keys() else None

    @property
    def api_name(self):
        return self._api_name

    @api_name.setter
    def api_name(self, name):
        if name in self.supported.keys():
            self._api_name = name
        return

    ### get_key(self):
#   Uses the api_name specified on initialization to fetch the environment variable name from api_info.json. It uses the name to get the environment variable.
#   Returns:
#       An API Key specified in the .env file. 

    def get_key(self):
        # if token/login return account info: key name for server, token for client
        key = self.supported.get(self.api_name).get('key', None)
        if key is None:
            return
        elif key == 'public':
            return key
        else: 
            return os.environ.get(key)

    def get_oauth_info(self):
        fields = self.supported.get(self.api_name).get('oauth_info', None)
        if fields is None:
            return NotImplemented
        info = {}
        for field, value in fields.items():
            info.update({field: os.environ.get(value)})
        return info

    ### get_api(self):
#   Returns:
#       The class for the API. Each API has the functions specified in the tt_wrapper_api.py so the functionality is uniform and doesn’t change how we fulfill a callback. 

    def get_api(self):
        if self.api_name == 'alpha_vantage':
            return alpha_vantage_tt.AlphaVantage()
        elif self.api_name == 'yahoo_finance':
            return yahoo_finance_tt.YahooFinance()
        else:
            return NotImplemented

### get_all_market_data(self, **kwargs)
#   I use kwargs here instead, incase that we wanted to change/add parameters of the abstract get_all_market_data specified in the tt_wrapper_api.py. It adds the API key to the argument so that it can fetch the data / construct the session. 
#   Returns:
#       CSV formatted data, pandas.to_csv() or csv package, or any whatever can output csv formatted data.
    def get_all_market_data(self, **kwargs):
        try:
            api = self.get_api()
            key = self.get_key()
            if (api is NotImplemented) or (key is NotImplemented):
                raise NotImplementedError
        except Exception as e:
            print(e)
        else:
            marketData = api.get_all_market_data(key=key, **kwargs)
            return marketData
        
### get_api_asset_types(self):
#   Returns:
#       The types of market history the api support

    def get_api_asset_types(self):
        return self.supported.get(self.api_name, None).get('types', None)