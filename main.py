from polymarket import Polymarket


def main():
    # Fetch data
    pmarket = Polymarket()
    markets = pmarket.get_markets(max_records=100)
    enabled_markets = markets.query("enable_order_book == True")

    for _, market in enabled_markets.iterrows():
        token_infos = pmarket.get_market_info(market)
        print(token_infos)


if __name__ == "__main__":
    main()
