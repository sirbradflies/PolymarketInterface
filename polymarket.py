"""
Class to interact with the Polymarket API
"""

import requests
import pandas as pd

QUERY_URL = "https://gamma-api.polymarket.com/query"


class Polymarket():

    def get_markets(self):
        return self.get_table("markets", fields=["conditionId"],
                              condition="enable_order_book = true")

    def get_series(self):
        return self.get_table("series", fields=["slug", "title"])

    def get_events(self):
        return self.get_table("events", fields=["slug", "title"])

    def get_categories(self):
        return self.get_table("categories", fields=["slug"])

    def get_table(self, table_name, fields, condition=None):
        condition_str = f"(where: \"{condition}\")" if condition else ""
        query = f"""
            query {{
                {table_name}{condition_str}{{
                    id,
                    {",\n".join(fields)}
                }}
            }}
            """
        data = self.send_query(query)
        table = pd.DataFrame.from_records(data[table_name]).set_index("id")
        return table

    def send_query(self, query):
        #print(f"Sending query: {query}")
        response = requests.post(QUERY_URL, json={'query': query})
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"Error: {response.status_code}")
