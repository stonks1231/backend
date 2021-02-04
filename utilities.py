import csv
import re
import os

BASE_DIR = os.environ.get("BASE_DIR")

def remove_punctuation(word):
    return re.sub(r'[^\w\s]', '', word)

def load_nasdaq_traded_tickers(filename=None):
    symbols = set()
    filename = f"{BASE_DIR}/symbols_directory/nasdaqtraded.txt"
    with open(filename, 'r', encoding='utf-8') as fh:
        reader = csv.reader(fh, delimiter='|')
        next(reader)
        for r in reader:
            symbols.add(r[1].lower())
    return symbols


def load_other_tickers(filename=None):
    symbols = set()
    filename = f"{BASE_DIR}/symbols_directory/otherlisted.txt"

    with open(filename, 'r', encoding='utf-8') as fh:
        reader = csv.reader(fh, delimiter='|')
        next(reader)
        for r in reader:
            symbols.add(r[0].lower())
    return symbols


def get_ticker_symbols():
    s1 = load_nasdaq_traded_tickers()
    s2 = load_other_tickers()

    return s1.union(s2)


if __name__ == '__main__':
    s = get_ticker_symbols()
    print(len(s))
