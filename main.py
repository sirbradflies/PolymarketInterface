from polymarket import Polymarket


def main():
    # Fetch data
    pmarket = Polymarket()
    markets = pmarket.get_markets()
    print(markets)
    series = pmarket.get_series()
    print(series)
    events = pmarket.get_events()
    print(events)
    categories = pmarket.get_categories()
    print(categories)


if __name__ == "__main__":
    main()
