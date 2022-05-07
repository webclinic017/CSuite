# ORDER MANAGEMENT SYSTEM
# Order object
from binance.enums import *
import CSuite.CSuite.CTrader as C


# Limit Order is utilised to ensure exact execution price
class LimitOrder:
    price, size = 0, 0
    symbol = ''
    stop, timeInForce = 0.0, 'GTC'
    params, client = None, None

    # API parameters
    side = None
    type = None

    def __init__(self, client, price, size, symbol, stop, timeInForce):

        if size > 0:
            self.side = SIDE_BUY
        else:
            self.side = SIDE_SELL

        self.stop = stop
        if stop == 0:
            self.type = ORDER_TYPE_LIMIT
        elif stop > price:
            self.type = ORDER_TYPE_TAKE_PROFIT_LIMIT
        elif stop < price:
            self.type = ORDER_TYPE_STOP_LOSS_LIMIT


        if timeInForce == 'GTC':
            self.timeInForce = TIME_IN_FORCE_GTC
        elif timeInForce == 'FOK':
            self.timeInForce = TIME_IN_FORCE_FOK
        elif timeInForce == 'IOC':
            self.timeInForce = TIME_IN_FORCE_IOC

        self.price, self.size, self.symbol = float(price), size, symbol
        self.client = client

    # Verifies the order against pre-set filters internally (supports custom logic)
    def verify(self, ledger):

        def verify_price():
            ref_price = float(self.client.get_avg_price(symbol=self.symbol)['price'])
            #print(type(self.price))
            if (self.price < ref_price*self.params['up']) and (self.price > ref_price*self.params['down']):
                return True
            else:
                return False

        def verify_notional():
            if self.price * abs(self.size) > self.params['minNotional']:
                return True
            else:
                return False

        def verify_qty():
            if (abs(self.size) > self.params['minQty']) and (abs(self.size) < self.params['maxQty']):
                return True
            else:
                return False

        self.params = ledger.loc[self.symbol]

        if verify_price():
            if verify_notional():
                if verify_qty():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    # Runs verification and submits
    def verified_submit(self, ledger):
        if self.verify(ledger):
            self.submit()
            return True
        else:
            return False

    # Submits TEST order to the exchange which can pass baseline parameters faster than verify()
    def test(self):
        if self.stop == 0:
            self.stop = None
        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=self.timeInForce, stopPrice=self.stop)

    # Submits the order to the exchange
    def submit(self):
        if self.stop == 0:
            self.stop = None
        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=self.timeInForce, stopPrice=self.stop)


# Market Orders enable access to immediate liquidity
class MarketOrder:
    size = 0
    symbol = ''
    stop = 0.0
    params, client = None, None

    # API parameters
    side = None
    type = None

    def __init__(self, client, size, symbol, stop=0):

        self.client = client
        self.size, self.symbol = size, symbol
        self.price = float(self.client.get_avg_price(symbol=self.symbol)['price'])

        if size > 0:
            self.side = SIDE_BUY
        else:
            self.side = SIDE_SELL

        self.stop = stop
        if stop == 0:
            self.type = ORDER_TYPE_MARKET
        elif stop > self.price:
            self.type = ORDER_TYPE_TAKE_PROFIT
        elif stop < self.price:
            self.type = ORDER_TYPE_STOP_LOSS

    def verify(self, ledger):

        def verify_notional():
            if self.price * abs(self.size) > self.params['minNotional']:
                return True
            else:
                return False

        def verify_qty():
            if (abs(self.size) > self.params['minQty']) and (abs(self.size) < self.params['maxQty']):
                return True
            else:
                return False

        self.params = ledger.loc[self.symbol]

        if verify_notional():
            if verify_qty():
                return True
            else:
                return False
        else:
            return False

    def verified_submit(self, ledger):
        if self.verify(ledger):
            self.submit()
            return True
        else:
            return False

    def test(self):
        if self.stop == 0:
            self.stop = None

        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), stopPrice=self.stop)

    def submit(self):
        if self.stop == 0:
            self.stop = None

        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), stopPrice=self.stop)


# Post Orders are aimed at market makers looking to cross with market contra
class PostOrder:
    price, size = 0, 0
    symbol = ''
    timeInForce = 'GTC'
    params, client = None, None

    # API parameters
    side = None
    type = None

    def __init__(self, client, price, size, symbol, timeInForce):

        if size > 0:
            self.side = SIDE_BUY
        else:
            self.side = SIDE_SELL

        self.type = ORDER_TYPE_LIMIT_MAKER


        if timeInForce == 'GTC':
            self.timeInForce = TIME_IN_FORCE_GTC
        elif timeInForce == 'FOK':
            self.timeInForce = TIME_IN_FORCE_FOK
        elif timeInForce == 'IOC':
            self.timeInForce = TIME_IN_FORCE_IOC

        self.price, self.size, self.symbol = float(price), size, symbol
        self.client = client

    def verify(self, ledger):

        def verify_price():
            ref_price = float(self.client.get_avg_price(symbol=self.symbol)['price'])
            #print(type(self.price))
            if (self.price < ref_price*self.params['up']) and (self.price > ref_price*self.params['down']):
                return True
            else:
                return False

        def verify_notional():
            if self.price * abs(self.size) > self.params['minNotional']:
                return True
            else:
                return False

        def verify_qty():
            if (abs(self.size) > self.params['minQty']) and (abs(self.size) < self.params['maxQty']):
                return True
            else:
                return False

        self.params = ledger.loc[self.symbol]

        if verify_price():
            if verify_notional():
                if verify_qty():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def verified_submit(self, ledger):
        if self.verify(ledger):
            self.submit()
            return True
        else:
            return False

    def test(self):
        return self.client.create_test_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=None)

    def submit(self):
        return self.client.create_order(symbol=self.symbol, side=self.side, type=self.type, quantity=abs(self.size), price=str(self.price), timeInForce=None)


# The OrderEngine is a module used to handle frequent execution in a certain pair,
# it acts as a wrapper for environment variables (tickSize) and API objects (Client).
class OrderEngine:
    client, ticker = None, ''
    ledger = None

    def __init__(self, client, ticker, ledger):
        self.client = client
        self.ticker = ticker
        self.ledger = ledger
        return

    # Builds a simple order of type 'LMT' or 'MKT'
    def order(self, type, size, price=0, stop=0, timeInForce='GTC'):

        if type == 'LMT' and price != 0:
            tmp_order = LimitOrder(self.client, price, size, self.ticker, stop, timeInForce)
        elif type == 'MKT':
            tmp_order = MarketOrder(self.client, size, self.ticker, stop)
        else:
            return False

        # Sends the Order to the exchange
        def send():
            return tmp_order.submit()

        # Sends a test order to the exchange
        def test():
            return tmp_order.test()

        return tmp_order

    # Runs the Tick-Match Algorithm, need pass only size and preferably distance
    def tick_match(self, size, distance=5, retry=10, refresh=2):
        return C.tick_match(self.client, self.ticker, float(size),
                            float(self.ledger.loc[self.ticker]['tickSize']), distance, retry, refresh)

    # Runs the Mid-Point Match Algorithm which requires only size input
    def midpoint_match(self, size, retry=10):
        return C.midpoint_match(self.client, self.ticker, float(size),
                                float(self.ledger.loc[self.ticker]['tickSize']), retry=retry)

