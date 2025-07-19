import requests
from bs4 import BeautifulSoup
import config
import csv

def extract_nutrition(soup):
    # 栄養成分を抽出
    nutrition = []
    tbody_ul = soup.select('ul.tbody')
    
    if not tbody_ul:
        return nutrition
    
    # 各liタグを処理
    for li in tbody_ul[0].select('li'):
        dt = li.select('dt')
        dd = li.select('dd')
        
        if dt and dd:
            dt_text = dt[0].text.strip()
            dd_text = dd[0].text.strip()
            
            # 炭水化物の場合、ネストしたulの糖質と食物繊維を処理
            if dt_text == config.CARBO:
                nested_ul = li.select('ul')
                if nested_ul:
                    for nested_li in nested_ul[0].select('li'):
                        nested_dt = nested_li.select('dt')
                        nested_dd = nested_li.select('dd')
                        if nested_dt and nested_dd:
                            nutrition.append(f"{nested_dt[0].text.strip()}：{nested_dd[0].text.strip()}")
            else:
                nutrition.append(f"{dt_text}：{dd_text}")
    return nutrition

def fetch_and_parse(url):
    """
    各スイーツの商品名と栄養成分を抽出
    戻り値：2つをまとめた辞書型
    """
    lawson_resp = requests.get(url, headers=config.HEADERS)
    lawson_resp.raise_for_status()
    lawson_resp.encoding = 'utf-8'
    lawson_html = lawson_resp.text
    lawson_soup = BeautifulSoup(lawson_html, 'html.parser')

    # 商品名を抽出
    h2 = lawson_soup.select('div.rightBlock h2.ttl')
    product_name = h2[0].text.replace('\u3000', ' ')

    # 栄養成分を抽出
    nutrition = extract_nutrition(lawson_soup)

    # 栄養成分を辞書型に変換
    dict_nutrition = {product_name:{}}
    for nutrient in nutrition:
        list = nutrient.split('：')
        dict_nutrition[product_name].update({list[0]:list[1]})

    return dict_nutrition

def fetch_lawson_products(list_url, domain = 'https://www.lawson.co.jp'):
    """
    ローソンの一覧ページから商品の詳細URLを取得する
    """

    resp = requests.get(list_url, headers=config.HEADERS)
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    urls = [
        a['href']
        for a in soup.select('ul.col-4.heightLineParent a')
    ]

    # 栄養成分の抽出
    product_list = []
    for url in urls:
        product_list.append(fetch_and_parse(domain + url))
    
    # カラム抽出
    values = next(iter(product_list[0].values()))
    nutrient_col = list(values.keys())
    
    # CSVファイル作成
    with open(config.LAWSON, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['商品名'] + nutrient_col)
        writer.writeheader()
        
        for product_item in product_list:
            for product_name, nutrition_data in product_item.items():
                row = {'商品名': product_name}
                row.update(nutrition_data)
                writer.writerow(row)
    return 0

if __name__ == '__main__':
    sej_url = 'https://www.lawson.co.jp/recommend/original/dessert/'
    fetch_lawson_products(sej_url)