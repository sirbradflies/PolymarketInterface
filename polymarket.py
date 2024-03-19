"""
Class to interact with the Polymarket API
"""
import numpy as np
import pandas as pd
import requests_cache

QUERY_URL = "https://clob.polymarket.com/"
HEADER = {"Accept-Encoding": "gzip",
          "Content-Type": "application/json",
          "Content-Encoding": "gzip"}


class Polymarket():
    def __init__(self):
        self.session = requests_cache.CachedSession(expire_after=360)

    def get_markets(self, condition_id=None, *args, **kwargs):
        return self.get_table(f"markets/{condition_id}", *args, **kwargs) if condition_id \
            else self.get_table("markets", *args, **kwargs)

    def get_price(self, token_id, side):
        price_dict = self.send_query(QUERY_URL+"price", params={"token_id": token_id, "side": side})
        return float(price_dict["price"]) if "price" in price_dict else np.nan

    def get_simplified_markets(self, *args, **kwargs):
        return self.get_table("simplified-markets", *args, **kwargs)

    def get_trades(self, *args, **kwargs):
        return self.get_table("trades", *args, **kwargs)

    def get_book(self, token_id, *args, **kwargs):
        return self.get_table("book", params={"token_id": token_id}, *args, **kwargs)

    def get_table(self, table_name, params=None, max_retries=3, max_records=np.inf):
        next_cursor = None
        data = pd.DataFrame()
        retries = 0
        while next_cursor != "LTE=" and len(data) < max_records and retries < max_retries:
            try:
                response = self.send_query(QUERY_URL+table_name, next_cursor, params)
                next_cursor = response["next_cursor"] if "next_cursor" in response else "LTE="
                new_data = pd.DataFrame.from_records(response["data"]) \
                    if "data" in response else pd.Series(response)
                data = pd.concat([data, new_data], axis="rows")
            except Exception as e:
                retries += 1
                print(f"{e}\nRetrying ({retries}/{max_retries})")
        return data

    #TODO: Add cache to avoid re-fetching the same data
    def send_query(self, url, next_cursor=None, params=None):
        if not params: params = {}
        if next_cursor: params["next_cursor"] = next_cursor
        print(f"Sending request to {url} with params {params}")
        response = self.session.get(url, headers=HEADER, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")
