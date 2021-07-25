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
    # print("Website Token: " + token)

    now = dt.datetime.now(tz)
    # the required qid of HKEX is the timestamp of now times 1000
    qid = str(int(now.timestamp() * 1000))
    # print("Website qid: "+ qid)
    return token, qid


def get_option_raw_data(month, product):
    # month format {MMYYYY}
    token, qid = get_HKEX_token_and_qid()
    link = f'https://www1.hkex.com.hk/hkexwidget/data/getderivativesoption?lang=eng&token={token}&ats={product}&con={month}&fr=17100&to=37200&type=0&qid={qid}&callback=jQuery'

    r2 = requests.get(link, timeout=5)
    # Read by beautiful soup
    soup2 = bs(r2.text, 'html.parser')
    soup2 = soup2.text[soup2.text.find('{'):-1]

    raw = json.loads(soup2)
    return raw

def request_option_single_month_data(month, product):
    raw = get_option_raw_data(month, product) # get raw_data from HKEX

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


def get_option_all_month(product):
    token, qid = get_HKEX_token_and_qid()
    month_list_link = f'https://www1.hkex.com.hk/hkexwidget/data/getoptioncontractlist?lang=eng&token={token}&ats={product}&type=0&qid={qid}&callback=jQuery'
    session = requests.session()

    month_list_r = session.get(month_list_link, timeout=5)
    month_list_soup = bs(month_list_r.text, 'html.parser')
    month_list_soup = month_list_soup.text[month_list_soup.text.find('{'):-1]
    month_list_raw = json.loads(month_list_soup)

    month_df = pd.DataFrame(month_list_raw['data']['conlist'])  # Turn into dataframe
    return month_df

def get_option_all_month_data(month, product,from_='null',to_='null'):
  # Define function for downloading option data
  # Step1: from_ and to_ are inputs for hang seng index min and max range, which are difference among contract months, 'null' are the default values
  # if we input 'null' for from_ and to_, we will get the suggested min and max index range from the link
  # Step2: We then plug in the suggested range to the api link again to get the option data for all months

  token, qid = get_HKEX_token_and_qid()
  api_link =f'https://www1.hkex.com.hk/hkexwidget/data/getderivativesoption?lang=eng&token={token}&ats={product}&con={month}&fr={from_}&to={to_}&type=0&qid={qid}&callback=jQuery'
  api_r=requests.get(api_link,timeout=5)
  api_soup=bs(api_r.text, 'html.parser')
  api_soup=api_soup.text[api_soup.text.find('{'):-1]
  api_raw=json.loads(api_soup)
  return api_raw


def request_option_bulk_month_data(product):

    month_df = get_option_all_month(product)

    for month in month_df['id']:
        print(f'Downloading {month}')
        get_index_range = get_option_all_month_data(month, product)  # Step1
        min_index, max_index = get_index_range['data']['min'].replace(',', ''), get_index_range['data']['max'].replace(
            ',', '')
        api_raw = get_option_all_month_data(month,product, from_=min_index, to_=max_index)  # Step2

        # Create empty dicts with a new column: 'months'
        dicts = {'month':[], 'Strike': [], 'Call_bid': [], 'Call_ask': [], 'Call_last': [], 'Call_vol': [], 'Call_oi': [],
                 'Call_iv': [], 'Put_bid': [],'Put_ask': [], 'Put_last': [], 'Put_vol': [], 'Put_oi': [], 'Put_iv': []}
        for row in api_raw['data']['optionlist']:
            strike = row['strike']
            dicts['Strike'].append(strike)  # append strike price data into 'strike' column in the dict
            dicts['month'].append(month)
            for call_data, call_col in zip(row['c'].values(), [*dicts.keys()][2:8]):  # for call option data
                dicts[call_col].append(call_data)
            for put_data, put_col in zip(row['p'].values(), [*dicts.keys()][8:]):  # for put option data
                dicts[put_col].append(put_data)

        final = pd.DataFrame(dicts)
        # Save all months files to csv
        final.to_csv(f'{product}_option_data_{month}.csv')
        print(final)

