import yfinance as yf
import APIs.api_wrapper_tt as tt
import pandas as pd

class YahooFinance(tt.TTApiWrapper):

    def __init__(self):
        super().__init__(name='yahoo_finance')
        self.dtable = self.create_dtable()

    def create_session(self, key, type_, symbol):
        if (key == 'public') and (type_ != 'cc'):
            self.session = yf.Ticker(ticker=symbol)
        return

    def create_dtable(self):
        dtable = {
            'month': '1mo',
            'week': '1wk',
            'day': '1d'
        }
        return dtable

    def get_all_market_data(self, key, symbol, type_, timeframe, keep_alive=False, **kwargs):
        self.create_session(key=key, type_=type_, symbol=symbol)
        interval = self.dtable.get(timeframe)
        try:
            data = self.session.history(period='max', interval=interval)
        except Exception as e:
            raise RuntimeError
        else:
            if not keep_alive:
                self.delete_session()
            df = self.clean(type_=type_, data=data)
            return df.to_csv(index=False)

    def get_most_recent_data(self, key, symbol, type_, timeframe, **kwargs):
        return

    def clean(self, type_, data):
        df = data.reset_index()
        df = df.rename(columns={
            'Date': 'date', 
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        df.drop(columns=[
            'Dividends',
            'Stock Splits'], inplace=True
            )
        return df
        