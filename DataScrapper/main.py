from DataScrapper.hkex_option import *


def main():
    df = request_option_single_month_data('082021', 'HSI')
    df.to_csv('option_data.csv')


if __name__ == "__main__":
    main()