import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt


class hkex_CBBC_data():

    def __init__(self):
        a = 0

    def get_CBBC_zip_from_hkex(self, url, save_name, chunk_size=128):
        r = requests.get(url, stream=True)
        # Write the file as .zip and save as {save_name}
        with open(save_name, 'wb') as output:
            for chunk in r.iter_content(chunk_size=chunk_size):
                output.write(chunk)

    def get_CBBCbulk_zip_from_hkex(self, start_month, end_month, combine):  # include combine to excel function
        datelist = pd.date_range(start=start_month, end=end_month, freq='M')
        datelist = [d.strftime("%Y%m") for d in datelist]

        for month in datelist:
            print(f"Downloading {month} data")
            self.get_CBBC_zip_from_hkex(f'https://www.hkex.com.hk/eng/cbbc/download/CBBC{month[-2:]}.zip',f'CBBC_{month}.zip', chunk_size=128)
        if combine == "Y":
            cbbc_full = pd.DataFrame()
            for month in datelist:
                print('Appending ', month)
                raw = pd.read_csv(f'CBBC_{month}.zip', compression='zip', header=0, sep='\t', encoding='utf-16')
                raw = raw[:-3]
                cbbc_full = cbbc_full.append(raw)
            cbbc_full.to_csv("cbbc_full" + "_" + str(start_month) + "_" + str(end_month) + '.csv')
            print(cbbc_full)
            return cbbc_full


if __name__ == "__main__":
    CBBC = hkex_CBBC_data()
    cbbc_full = CBBC.get_CBBCbulk_zip_from_hkex("2021-01-01", "2021-08-01", 'Y')