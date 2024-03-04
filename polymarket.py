"""
Class to interact with the Polymarket API
"""
import numpy as np
import requests
import pandas as pd

QUERY_URL = "https://clob.polymarket.com/"
HEADER = {"User-Agent": "py_clob_client",
          "Accept": "*/*",
          "Connection": "keep-alive",
          "Content-Type": "application/json",
          "Accept-Encoding": "gzip"}


class Polymarket():

    def get_markets(self, condition_id=None, *args, **kwargs):
        return self.get_table("markets") if condition_id is None \
            else self.get_table(f"markets/{condition_id}", *args, **kwargs)

    def get_simplified_markets(self, *args, **kwargs):
        return self.get_table("simplified-markets", *args, **kwargs)

    def get_trades(self, *args, **kwargs):
        return self.get_table("trades", *args, **kwargs)

    def get_book(self, token_id, *args, **kwargs):
        return self.get_table("book", params={"token_id": token_id}, *args, **kwargs)

    def check_arbitrage(self, tokens):
        book_asks = []
        for token in tokens:
            book = self.get_book(token["token_id"])
            asks = book["asks"] if book is not None else []
            book_asks += [asks[-1]] if len(asks)>0 \
                else [{"price": np.nan, "size": np.nan}]
        book_asks = pd.DataFrame.from_records(book_asks)
        book_asks = book_asks.apply(pd.to_numeric, errors="ignore")
        return book_asks["price"].sum(skipna=False)

    def get_table(self, table_name, params=None, max_retries=3, max_records=np.inf):
        next_cursor, data = None, None
        retries = 0
        while next_cursor != "LTE=":
            try:
                response = self.send_query(QUERY_URL+table_name, next_cursor, params)
                next_cursor = response["next_cursor"] if next_cursor in response else "LTE="
                new_data = pd.DataFrame.from_records(response["data"]) \
                    if "data" in response else pd.Series(response)
                data = pd.concat([data, new_data], axis="rows")
            except Exception as e:
                retries += 1
                print(f"{e}\nRetrying ({retries}/{max_retries})")
            if (data is not None and len(data) >= max_records) or retries >= max_retries: break
        return data

    def send_query(self, url, next_cursor=None, params=None):
        if params is None:
            params = {}
        if next_cursor is not None:
            params["next_cursor"] = next_cursor
        #print(f"Sending request to {url} with params {params}")
        response = requests.get(url, headers=HEADER, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")
