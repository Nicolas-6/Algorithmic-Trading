# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 22:01:27 2023

@author: 06nic
"""

# create algorithmic strategy for forex based on price values
# let's assume that we are investing in some major forex EUR/USD, GBP/USD, JPY/USD, EUR/GBP
# the goal of this algorithm will be to equilibrate the weight of the portfolio so that we can maximize our returns 

# we can evaluate some factors with points as 
# _ if the price if the upper quartile using the last 30 days price -1 if lower quartile +1
# _ if the last change in price is greater than +2% then -1 if lower than -2% +1
# _ if the last 5 days average price is > than last price  +1  else -1
# _ if last month annual volatility is more than halth 5 years volatility +1 if not -1



def get_data (tickers_list, end_date):
    import yfinance as yf
    import datetime as dt
    tdelta = (end_date-dt.timedelta(days=365*5)).date()
    tdelta = str(tdelta)
    data = yf.download(tickers_list, start=tdelta, end=str(end_date.date()))['Close']
    return data

    
def calculations_metrics (tickers_list, end_date):
    import numpy as np
    import pandas as pd
    #last price
    data = get_data(tickers_list, end_date)
    lprice = data.iloc[-1,:]
    data_chg = data.pct_change()    
    lchange = data_chg.iloc[-1,:]
    uquartile=pd.Series(np.quantile(np.array(data.dropna()),0.75,axis=0),index=tickers_list)
    lquartile = pd.Series(np.quantile(np.array(data.dropna()),0.25,axis=0),index=tickers_list)
    avg7lprice =pd.Series( np.average(data.dropna().iloc[-7:,:],axis=0),index=tickers_list)
    lmont_vol = pd.Series(np.std(data.dropna().iloc[-30:,:],axis=0),index=tickers_list)
    _5yvol = pd.Series(np.std(data.dropna().iloc[-365*60:,:],axis=0),index=tickers_list)
    tickers = pd.Series(tickers_list,index=tickers_list)
    data_metrics = pd.concat([tickers,lprice,lchange,uquartile,lquartile,avg7lprice,lmont_vol,_5yvol],axis=1,ignore_index=True)
    return data_metrics


def score_table(data):
    data['score']=""
    for i, row in data.iterrows():
        score = 0
        if row['Last_price'] >= row['Upper_Quartile_30']:
            score +=1
        if row['Last_price'] <= row['Lower_Quartile_30']:
            score+= -1
        if row['Last_change_%']>0.01:
            score+=1
        if row['Last_change_%']< -0.01:  
            score+=-1
        if row['Last_7avgPrice'] >row['Last_price']:
            score+=1
        else:
            score+=-1
        if row['5Y_vol']/row['Last_month_vol'] < 2:
            score+=1
        data.loc[i,'score']=score
    return data

def get_weights (tickers_list,end_date):
    import pandas as pd
    dmcolumns = ['ticker','Last_price', "Last_change_%",'Upper_Quartile_30','Lower_Quartile_30',"Last_7avgPrice","Last_month_vol","5Y_vol"]
    dmetrics = calculations_metrics(tickers_list,end_date)
    dmetrics.columns = dmcolumns
    dmetrics = score_table(dmetrics)
    total_score= sum(abs(dmetrics['score']))
    if total_score!=0:
        dmetrics['weight']=dmetrics['score']/total_score
    else:
        dmetrics['weight']= 0
        
    return list(dmetrics['weight'])
    
    
#Backtesting
#today price should change to have the weighting each day
#Try backtesting on January Month
# l'idée c'est d'avoir une colonne P&L 
def backtesting(tickers_list,nb_days,investment,freq_update):
    import datetime as dt
    import pandas as pd
    import numpy as np
    import math
    date_range = list(reversed([dt.datetime.today() -dt.timedelta(i) for i in range(1,nb_days+1)]))
    label_price = ["price_"+i for i in  tickers_list]
    label_weights = ['weight_'+i for i in  tickers_list]
    result_table = pd.DataFrame(columns=['Date']+label_price+ label_weights + ['P&L'], data = np.zeros((len(date_range),len(tickers_list)*2+2)))
    result_table.iloc[:,:]= ""
    last_price= [0]*len(tickers_list)
    for idx, end_date in enumerate(date_range):
        row = []
        last_price= list(get_data(tickers_list,end_date).iloc[-1,:])
        # ajouter la fréquence d'actualisation ici
        
        if idx ==0 :
            p_l = [investment]
            weigths = get_weights (tickers_list,end_date)
        else:
            if (idx+1) % freq_update ==0:
                weigths = get_weights (tickers_list,end_date)
                
            p_l = [p_l[0] + sum([p_l[0]*abs(w_)*((np/lp-1)*math.copysign(1, w_)) for w_,np,lp in zip (weigths_, last_price, last_price_)])]
        weigths_ = weigths
        last_price_ = last_price
        result_table.iloc[idx,:]=[end_date.date()]+last_price+weigths+p_l
        
        result_table.set_index(result_table['Date'],inplace=True)
    return result_table
            
tickers = sorted(['EURUSD=X','GBPEUR=X','JPYUSD=X','CHFJPY=X','CAD=X'])

results = backtesting(tickers,200,1000,7)
results.set_index(results['Date'],inplace=True)
import matplotlib.pyplot as plt
plt.plot(results['P&L'])   
plt.xticks(rotation=45)
plt.ylabel("P&L ($) ")
        
        
    