from abc import ABC, abstractmethod

class TTApiWrapper(ABC):

    ## TODO add token/login, logging
    def __init__(self, name):
        self.name = name
        self.session = None
        self.dtable = None
        
    ## TODO asyncio
    @abstractmethod
    def get_all_market_data(self, key, symbol, type_, timeframe, **kwargs):
        return ## csv format 

    @abstractmethod
    def get_most_recent_data(self, key, symbol, type_, timeframe, **kwargs):
        return

    @abstractmethod
    def create_session(self, key, type_):
        return

    @abstractmethod
    def create_dtable(self):
        return

    @abstractmethod
    def clean(self, *args):
        return

    def delete_session(self):
        del self.session, self.dtable
        self.session, self.dtable = None, None