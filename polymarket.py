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
    def __init__(self, session_verify=True, session_expire_after=None):
        self.session_verify = session_verify
        self.session_expire_after = session_expire_after
        self.session = requests_cache.CachedSession(expire_after=self.session_expire_after)

    def get_market_info(self, market):
        token_infos = []
        for token in market["tokens"]:
            token_id = token["token_id"]
            book = self.get_book(token_id)
            bid = float(book["bids"][-1]["price"]) if len(book["bids"]) > 0 else np.nan
            ask = float(book["asks"][-1]["price"]) if len(book["asks"]) > 0 else np.nan
            market_info = {"question": market["question"],
                           "outcome": token["outcome"],
                           "condition_id": market["condition_id"],
                           "token_id": token_id,
                           "end_date_iso": market["end_date_iso"],
                           "bid": bid,
                           "ask": ask}
            token_infos += [market_info]
        token_infos = pd.DataFrame.from_records(token_infos)
        token_infos["end_date_iso"] = pd.to_datetime(token_infos["end_date_iso"]).dt.tz_localize(None)
        token_infos.eval("spread = ask - bid", inplace=True)
        token_infos["days_to_end"] = (token_infos["end_date_iso"] - pd.Timestamp.now()).dt.days
        return token_infos

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
        book = self.send_query(QUERY_URL + "book", params={"token_id": token_id})
        return pd.Series(book)

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

    def send_query(self, url, next_cursor=None, params=None):
        if not params: params = {}
        if next_cursor: params["next_cursor"] = next_cursor
        print(f"Sending request to {url} with params {params}")
        response = self.session.get(url, headers=HEADER, params=params, verify=self.session_verify)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")
