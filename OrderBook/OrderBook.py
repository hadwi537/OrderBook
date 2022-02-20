from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
from dataclasses import replace


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

    @staticmethod
    def eat_book(
        ps_pairs: PriceSizePairs, 
        shares: int) -> Tuple[DollarsAndShares, PriceSizePairs]:
        '''
        Method for LO and MO interaction with OrderBook
        '''
        rem_shares: int = shares
        dollars: float = 0
        for i, d_s in enumerate(ps_pairs):
            this_price: float = d_s.dollars
            this_shares: int = d_s.shares
            dollars += this_price * min(rem_shares, this_shares)
            if rem_shares < this_shares:
                return(
                    DollarsAndShares(dollars=dollars, shares=shares),
                    [DollarsAndShares(
                        dollars=this_price,
                        shares=this_shares - rem_shares
                    )] + list(ps_pairs[i+1:])
                )
            else:
                rem_shares -= this_shares
        return (
            DollarsAndShares(dollars=dollars, shares=shares - rem_shares),
            []
        )
    
    def sell_limit_order(self, price: float, shares: int) -> \
            Tuple[DollarsAndShares, OrderBook]:
        
        index: Optional[int] = next((i for i, d_s
                                    in enumerate(self.descending_bids)), None)
        eligible_bids: PriceSizePairs = self.descending_bids \
            if index is None else self.descending_bids[:index]
        ineligible_bids: PriceSizePairs = [] if index is None else \
            self.descending_bids[index:]

        d_s, rem_bids = OrderBook.eat_book(eligible_bids, shares)
        new_bids: PriceSizePairs = list(rem_bids) + list(ineligible_bids)
        rem_shares: int = shares - d_s.shares

        if rem_shares > 0:
            new_asks: list[DollarsAndShares] = list(self.ascending_asks)
            index1: Optional[int] = next((i for i, d_s
                                        in enumerate(new_asks)
                                        if d_s.dollars >= price), None)
        
            if index1 is None:
                new_asks.append(DollarsAndShares(
                    dollars=price,
                    shares=rem_shares
                ))
            elif new_asks[index1].dollars != price:
                new_asks.insert(index1, DollarsAndShares(
                    dollars=price,
                    shares=rem_shares
                ))
            else:
                new_asks[index1] = DollarsAndShares(
                    dollars=price,
                    shares=new_asks[index1].shares + rem_shares
                )
            return d_s, OrderBook(
                ascending_asks=new_asks,
                descending_bids=new_bids
            )
        else:
            return d_s, replace(
                self,
                descending_bids=new_bids
            )
    
    def sell_market_order(
        self, 
        shares: int
    ) -> Tuple[DollarsAndShares, OrderBook]:
        d_s, rem_bids = OrderBook.eat_book(
            self.descending_bids, 
            shares
        )
        return (d_s, replace(self, descending_bids=rem_bids))

    def pretty_print_order_book(self) -> None:
        from pprint import pprint
        print()
        print("Bids")
        pprint(self.descending_bids)
        print()
        print("Asks")
        print()
        pprint(self.ascending_asks)
        print()
    
    def display_order_book(self) -> None:
        import matplotlib.pyplot as plt

        bid_prices = [d_s.dollars for d_s in self.descending_bids]
        bid_shares = [d_s.shares for d_s in self.descending_bids]
        if self.descending_bids:
            plt.bar(bid_prices, bid_shares, color='blue')

        ask_prices = [d_s.dollars for d_s in self.ascending_asks]
        ask_shares = [d_s.shares for d_s in self.ascending_asks]
        if self.ascending_asks:
            plt.bar(ask_prices, ask_shares, color='red')

        all_prices = sorted(bid_prices + ask_prices)
        all_ticks = ["%d" % x for x in all_prices]
        plt.xticks(all_prices, all_ticks)
        plt.grid(axis='y')
        plt.xlabel("Prices")
        plt.ylabel("Number of Shares")
        plt.title("Order Book")
        #plt.xticks(x_pos, x)
        plt.show()

if __name__ == "__main__":
    
    from numpy.random import poisson

    bids: PriceSizePairs = [DollarsAndShares(
        dollars=x,
        shares=poisson(100. - (100 - x) * 10)
    ) for x in range(100, 90, -1)]
    asks: PriceSizePairs = [DollarsAndShares(
        dollars=x,
        shares=poisson(100. - (x - 105) * 10)
    ) for x in range(105, 115, 1)]
    #initalise a testing OrderBook
    ob0 = OrderBook = OrderBook(descending_bids=bids, ascending_asks=asks)