# -*- coding: utf-8 -*-
"""
Created on Sat May 21 18:29:36 2022

@author: nicolas
"""

# library essential
import time
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
from statistics import NormalDist
start = dt.date.today()


#logging in Iqoption
from iqoptionapi.stable_api import IQ_Option
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
Iq=IQ_Option("email","password")
check, reason=Iq.connect()
print(check, reason)
Iq.get_balance()
balance_type="PRACTICE" #MODE="PRACTICE"/"REAL"/"TOURNAMENT"
Iq.change_balance(balance_type)



Record_order = pd.DataFrame(index= np.arange(1*60*24), columns=["Date", "orderType","OrderId", "check_order", "Price"] )
average_change = BTC_change.mean()
std_change = BTC_change.std()
var70 = NormalDist().inv_cdf(0.30) #inverse cumulative probability function
worst_change_30 = average_change + std_change * var70

"""
My idea is to find trend.
So if my security varies more than variation of 70% , I follow the trend so I buy It 
And then I have a function called check gain that analyses previous trancastions and closes
thoses positions if I made profit

"""
Last_change>abs(worst_change_30) 

i=1 
y=0
while i == 1:
    BTC_data = yf.download("BTC-USD", start = start, interval= "1m")
    BTC_change = BTC_data["Adj Close"].pct_change().dropna()
    Last_change = BTC_change[-1]
    if Last_change>abs(worst_change_30):
        print ("Hey have a look", "Last_change is", Last_change, sep = "__", end=".")
        order("buy")
        
        y = y+1
    if Last_change < worst_change_30:
        # Sell Futures
        order("sell")
        y = y+1
    checkgain()
    time.sleep(60)

Iq.get_positions("crypto")
 print(Iq.get_positions("crypto"))
 
 
 # Function to buy or sell on IqOption
def order(buy_or_sell):
               
        # Buy Futures
        instrument_type="crypto"
        instrument_id="BTCUSD"
        side= buy_or_sell #input:"buy"/"sell"
        amount=1 #input how many Amount you want to pay

        #"leverage"="Multiplier"
        leverage= 2 #you can get more information in get_available_leverages()

        type="market"#input:"market"/"limit"/"stop"

        #for type="limit"/"stop"

        # only working by set type="limit"
        limit_price=None#input:None/value(float/int)

        # only working by set type="stop"
        stop_price=None#input:None/value(float/int)

        #"percent"=Profit Percentage
        #"price"=Asset Price
        #"diff"=Profit in Money

        stop_lose_kind="percent"#input:None/"price"/"diff"/"percent"
        stop_lose_value=95#input:None/value(float/int)

        take_profit_kind=None#input:None/"price"/"diff"/"percent"
        take_profit_value=None#input:None/value(float/int)

        #"use_trail_stop"="Trailing Stop"
        use_trail_stop=True#True/False

        #"auto_margin_call"="Use Balance to Keep Position Open"
        auto_margin_call=False#True/False
        #if you want "take_profit_kind"&
        #            "take_profit_value"&
        #            "stop_lose_kind"&
        #            "stop_lose_value" all being "Not Set","auto_margin_call" need to set:True

        use_token_for_commission=False#True/False

        check_order, order_id=Iq.buy_order(instrument_type=instrument_type, instrument_id=instrument_id,
                    side=side, amount=amount,leverage= leverage,
                    type=type,limit_price=limit_price, stop_price=stop_price,
                    stop_lose_value=stop_lose_value, stop_lose_kind=stop_lose_kind,
                    take_profit_value=take_profit_value, take_profit_kind=take_profit_kind,
                    use_trail_stop=use_trail_stop, auto_margin_call=auto_margin_call,
                    use_token_for_commission=use_token_for_commission)
        
        Record_order["Date"][y]=dt.date.today()
        Record_order["OrderId"][y]=order_id
        Record_order["orderType"][y] = buy_or_sell
        Record_order["check_order"][y]= check_order
        Record_order["Price"][y]= BTC_data["Adj Close"][-1]
        return  print(Iq.get_order(order_id), Iq.get_positions("crypto"), sep ="\n")
    
    Record_order.to_excel("record.xlsx")


# Function to close transaction and lock gains
def checkgain():
    numbergain = 0
    for x in range(len(Record_order["Price"])):
        LastPrice = BTC_data["Adj Close"][-1]
        if Record_order["orderType"][x] == "sell":
            if (LastPrice/Record_order["Price"][x])-1 < -0.02-(average_change - std_change * var70) :
                Iq.close_position(Record_order["OrderId"][x])
                numbergain = numbergain +1 
        else :
            if (LastPrice/Record_order["Price"][x])-1 > 0.02+(average_change - std_change * var70):
                Iq.close_position(Record_order["OrderId"][x])
                numbergain = numbergain +1
    return print( "we have", numbergain, "gains", sep = "  ")
            
                
