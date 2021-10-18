import apis.api_wrapper_tt as tt
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd


class AlphaVantage(tt.TTApiWrapper):

    def __init__(self):
        super().__init__(name='alpha_vantage')

    def create_session(self, key, type_, output_format='pandas'):
        if type_ == 'cc':
            self.session = CryptoCurrencies(key=key, output_format=output_format)
        elif type_ == 'tr':
            self.session = TimeSeries(key=key, output_format=output_format)
        elif type_ == 'fx':
            self.session = ForeignExchange(key=key, output_format=output_format)
        else:
            raise LookupError
        return self.create_dtable(type_=type_)

    def create_dtable(self, type_):
        if type_ == 'cc':
            self.dtable = {
                'month': self.session.get_digital_currency_monthly,
                'week': self.session.get_digital_currency_weekly,
                'day': self.session.get_digital_currency_daily,
                }
        elif type_ == 'tr':
            self.dtable = {
                'month': self.session.get_monthly,
                'week': self.session.get_weekly,
                'day': self.session.get_daily,
                'intraday': self.session.get_intraday_extended,
                }
        elif type_ == 'fx':
            self.dtable = {
                'month': self.session.get_currency_exchange_monthly,
                'week': self.session.get_currency_exchange_weekly,
                'day': self.session.get_currency_exchange_daily,
                'intraday': self.session.get_currency_exchange_intraday,
                }
        return

        
    ## TODO add clean functions for attributes using regex
    def get_all_market_data(self, key, symbol, type_, timeframe, keep_alive=False, **kwargs):
        try:

            if kwargs.get('output_format', False):
                self.create_session(key=key, type_=type_, output_format=kwargs['output_format'])
                del kwargs['output_format']
            else:
                self.create_session(key=key, type_=type_)

            func = self.dtable.get(timeframe, NotImplementedError)

            if type_ == 'cc':
                data, meta = func(symbol=symbol, market=kwargs.get('market', 'USD'))
            elif type_ == 'tr':
                data, meta = func(symbol=symbol, **kwargs)
            elif type_ == 'fx':
                to_symbol = kwargs.get('market', 'USD')
                if kwargs.get('market', False):
                    del kwargs['market']
                data = func(from_symbol=symbol, to_symbol=to_symbol, **kwargs)

        except Exception as e:
            print(f'Could\'t get market data: {type_}: {timeframe} from {self.name} is not supported.')
            print(e)
            return None

        else:
            if not keep_alive:
                self.delete_session()
            df = self.clean(type_=type_, data=data)
            return df.to_csv()
        
    def clean(self, type_, data):
        if type_ == 'cc':
            return self.clean_cc(data=data)
        elif type_ == 'fx':
            return self.clean_fx(data=data)
        elif type_ == 'tr':
            return self.clean_tr(data=data)

    def clean_cc(self, data):
        df = data.rename(columns={
            '1a. open (USD)': 'open', 
            '2a. high (USD)': 'high', 
            '3a. low (USD)': 'low', 
            '4a. close (USD)': 'close',
            '5. volume': 'volume',
            '6. market cap (USD)': 'market_cap'
            })
        df.drop(columns=[
            '1b. open (USD)',
            '2b. high (USD)',
            '3b. low (USD)',
            '4b. close (USD)',
            ], inplace=True)
        return df

    def clean_tr(self, data):
        print(data.columns)
        df = data.rename(columns={
            '1. open': 'open', 
            '2. high': 'high', 
            '3. low': 'low', 
            '4. close': 'close',
            '5. volume': 'volume'
        })
        return df

    def clean_fx(self, data):
        df = data.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close'
        })
        return df

    def get_most_recent_data(self, symbol, type_, timeframe, **kwargs):
        return NotImplemented

if __name__ == '__main__':
    av = AlphaVantage()
    av.get_all_market_data(symbol='ETH', type_='cc', timeframe='week')