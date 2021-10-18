from apis import alpha_vantage_tt
from apis import yahoo_finance_tt
import os
import json
import pathlib

## make sure to create and populate the .env file

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

    def get_api(self):
        if self.api_name == 'alpha_vantage':
            return alpha_vantage_tt.AlphaVantage()
        elif self.api_name == 'yahoo_finance':
            return yahoo_finance_tt.YahooFinance()
        else:
            return NotImplemented

    def get_all_market_data(self, **kwargs):
        try:
            api = self.get_api()
            key = self.get_key()
            if (api is NotImplemented) or (key is NotImplemented):
                raise NotImplementedError
        except Exception as e:
            print(e)
        else:
            return api.get_all_market_data(key=key, **kwargs)
        
    def get_api_asset_types(self):
        return self.supported.get(self.api_name, None).get('types', None)