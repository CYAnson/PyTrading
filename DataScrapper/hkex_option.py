import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import os
import datetime as dt
from datetime import datetime, timedelta
import json
import pytz

tz = pytz.timezone('Asia/Hong_Kong')

def get_HKEX_token_and_qid():
    link = 'https://www.hkex.com.hk/Market-Data/Futures-and-Options-Prices/Equity-Index/Hang-Seng-Index-Futures-and-Options?sc_lang=en#&product=HSI'

    # As HKEX webpage requires cookies so we use requests.session
    session = requests.session()
    # Get the html text from the webpage
    r = session.get(link, timeout=5)
    # Read by beautiful soup
    soup = bs(r.text, 'html.parser')
    # Extract the token required
    string = str(soup.find_all('script')[20])
    token_script = string.split(';')
    token = token_script[3].replace('\r\n', '').replace('return', '').replace('"', '').strip()
    print("Website Token: " + token)

    now = dt.datetime.now(tz)
    # the required qid of HKEX is the timestamp of now times 1000
    qid = str(int(now.timestamp() * 1000))
    print("Website qid: "+ qid)
    return token, qid

def request_option_raw_data(month):
    # month format {MMYYYY}
    token, qid = get_HKEX_token_and_qid()
    link2 = f'https://www1.hkex.com.hk/hkexwidget/data/getderivativesoption?lang=eng&token={token}&ats=HSI&con={month}&fr=17100&to=37200&type=0&qid={qid}&callback=jQuery'

    r2 = requests.get(link2, timeout=5)
    # Read by beautiful soup
    soup2 = bs(r2.text, 'html.parser')
    soup2 = soup2.text[soup2.text.find('{'):-1]

    raw = json.loads(soup2)
    return raw

def request_option_single_month(month):
    raw = request_option_raw_data(month) # get raw_data from HKEX

    # First define a empty dict with columns below, each contains a empty list
    dicts = {'Strike': [], 'Call_bid': [], 'Call_ask': [], 'Call_last': [], 'Call_vol': [], 'Call_oi': [], 'Call_iv': [], 'Put_bid': [],
             'Put_ask': [], 'Put_last': [], 'Put_vol': [], 'Put_oi': [], 'Put_iv': []}

    for row in raw['data']['optionlist']:
        strike = row['strike']
        dicts['Strike'].append(strike)  # append strike price data into 'strike' column in the dict
        for call_data, call_col in zip(row['c'].values(), [*dicts.keys()][1:7]):  # for call option data
            dicts[call_col].append(call_data)
        for put_data, put_col in zip(row['p'].values(), [*dicts.keys()][7:]):  # for put option data
            dicts[put_col].append(put_data)

    final = pd.DataFrame(dicts)  # Convert dict to Dataframe
    return final

