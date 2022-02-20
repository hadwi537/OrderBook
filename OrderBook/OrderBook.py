from dataclasses import dataclass
from tkinter.tix import Tree
from typing import Sequence


'''
Facilitates matching stock buyers with stock sellers

Buyers and sellers express intrest to trade by:
Bids (intent to buy)
asks (intent to sell)
known as limit orders
"limit" only interested in buying below a certain price levels
ea LO = (P, N) ; P = price, N = shares
=> buy LO (P, N) = willing to buy N shares at price <= P

Otehr type:
Market Order (MO)
states one intet to buy/sell N shares at the best possible price(S) available 
on OB at the time of MO submission
'''

@dataclass(frozen = True)
class DollarsAndShares: 
    '''
    Can represent an LO
    or pair of total dollors transacted when MO exectuted
    '''
    dollars: float
    shares: int
PriceSizePairs = Sequence[DollarsAndShares]

@dataclass(frozen=True)
class OrderBook:

    descending_bids: PriceSizePairs
    ascending_asks: PriceSizePairs

    def bid_price(self) -> float:
        return self.descending_bids[0].dollars
    
    def ask_price(self) -> float:
        return self.ascending_asks[0].dollars
    
    def mid_price(self) -> float:
        return (self.bid_price() + self.ask_price()) / 2
    
    def bid_ask_spread(self) -> float:
        return self.ask_price() - self.bid_price()

    def market_depth(self) -> float:
        return self.ascending_asks[-1].dollars - \
            self.descending_bids[-1].dollars

