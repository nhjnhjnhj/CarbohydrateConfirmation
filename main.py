from sej_fetcher import fetch_seven_eleven_products
from lawson_fetcher import fetch_lawson_products
import config
import concurrent.futures

def main():
    print('商品を並行取得中...')
    # 並行処理で各企業のフェッチャーを実行
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.URL_NUM) as executor:
        
        # 各タスクを並行実行
        sej_future = executor.submit(fetch_seven_eleven_products, config.SEJ_URL)
        lawson_future = executor.submit(fetch_lawson_products, config.LAWSON_URL)
        
        # 完了を待機
        concurrent.futures.wait([sej_future, lawson_future])
    print("Done")

if __name__ == '__main__':
    main()