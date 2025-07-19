from sej_fetcher import fetch_seven_eleven_products
from lawson_fetcher import fetch_lawson_products

def main():
    sej_url = 'https://www.sej.co.jp/products/a/cat/060010010000000/kanto/1/l100/'
    lawson_url = 'https://www.lawson.co.jp/recommend/original/dessert/'

    print('sej商品の取得中...')
    fetch_seven_eleven_products(sej_url)

    print('lawson商品の取得中...')
    fetch_lawson_products(lawson_url)

    print('Done')


if __name__ == '__main__':
    main()