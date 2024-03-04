from polymarket import Polymarket


def main():
    # Fetch data
    pmarket = Polymarket()
    markets = pmarket.get_markets(max_records=10000)
    enabled_markets = markets.query("enable_order_book == True")
    for _, market in enabled_markets.iterrows():
        arbitrage_value = pmarket.check_arbitrage(market["tokens"])
        print(f"{market["question"]} {arbitrage_value}")


if __name__ == "__main__":
    main()
