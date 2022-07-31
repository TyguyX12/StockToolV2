from abc import ABC, abstractmethod


### Abstract class used to normalize any api that we add. As long as we can fulfil these functions, we can add the api. It supports any kind of authentication using the session and dtable properties. The dtable can be used to specify the call for a given type_.

class TTApiWrapper(ABC):

    ## TODO add token/login, logging
    def __init__(self, name):
        self.name = name
        self.session = None
        self.dtable = None
        
    ## TODO asyncio
    ### Abstract get_all_market_data(self, key, symbol, type_, timeframe) 
#   This allows us to fetch the market data using the variables we collected through user interaction

    @abstractmethod
    def get_all_market_data(self, key, symbol, type_, timeframe, **kwargs):
        return ## csv format 

    @abstractmethod
    def get_most_recent_data(self, key, symbol, type_, timeframe, **kwargs):
        return

    ### Abstract create_session(self, key, type_)
#   API functions use this at their start so they can be authorized. Need to make this into a decorator.

    @abstractmethod
    def create_session(self, key, type_):
        return

    ### Abstract create_dtable(self)
#   The dtable maps the created session (self.session) to session functions (.get_week_exchange_history). You cannot store a function that depends on a session/connection (i.e., can’t do ForeignCurrency.get_week_exchange_history). You can use the dtable to extend any kind of session to any of its functions.

    @abstractmethod
    def create_dtable(self):
        return

    ### Abstract clean(self, *args)
#   Clean is used to normalize the returned data. You can use conditionals to extend its functionality and clean data more specifically if necessary. 

    @abstractmethod
    def clean(self, *args):
        return

    ### Abstract delete_session(self)
#   API functions use this at their end to delete their session. You can add a keep_alive parameter to optionally persist the session. That way, if we want to get a bunch of data, we don’t have to create new sessions for every call.

    def delete_session(self):
        del self.session, self.dtable
        self.session, self.dtable = None, None