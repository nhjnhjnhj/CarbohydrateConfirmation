import requests
from bs4 import BeautifulSoup
import config
import re
import csv

def extract_nutrition(soup):
    # 栄養成分を抽出
    resultset = soup.select('div.allergy table tbody ')
    detail = re.split(r'(<[^>]+>)', str(resultset[0]))
    for line in detail:
        if config.KCAL in line:
            nutrition = line.split('、')
    
    # 糖質と食物繊維の抽出も同時に行う
    processed = []
    for index, value in enumerate(nutrition):
        if config.CARBO in value:
            # 「（」が含まれていない場合は炭水化物を糖質に置換
            if '（' not in value:
                nutrition[index] = value.replace(config.CARBO, '糖質')
            else:
                carbohydrates = [nutrition[index], nutrition[index + 1]]
                for c in carbohydrates:
                    # 「（」以降を取り出す（糖質のみ）
                    if '（' in c:
                        part = c.split('（', 1)[1]
                    else:
                        part = c
                    # 末尾の「）」を除去
                    part = part.rstrip('）')
                    processed.append(part)
                nutrition[index] = processed[0]
                nutrition[index + 1] = processed[1]

    return nutrition

def fetch_and_parse(url):
    """
    各スイーツの商品名と栄養成分を抽出
    戻り値：2つをまとめた辞書型
    """
    sej_resp = requests.get(url, headers=config.HEADERS)
    sej_resp.raise_for_status()
    sej_html = sej_resp.text
    sej_soup = BeautifulSoup(sej_html, 'html.parser')

    # 商品名を抽出
    h1 = sej_soup.select('div.item_ttl h1')
    product_name = h1[0].text.replace('\u3000', ' ')

    # 栄養成分を抽出（糖質と食物繊維の処理も含む）
    nutrition = extract_nutrition(sej_soup)

    # 栄養成分を辞書型に変換
    dict_nutrition = {product_name:{}}
    for nutrient in nutrition:
        list = nutrient.split('：')
        dict_nutrition[product_name].update({list[0]:list[1]})

    return dict_nutrition

def fetch_seven_eleven_products(list_url, domain = 'https://www.sej.co.jp'):
    """
    セブンイレブンの一覧ページから商品の詳細URLを取得する
    """
    resp = requests.get(list_url, headers=config.HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    sejs_url = [
        a['href']
        for a in soup.select('div.flex_wrap figure a[href]')
    ]

    # 栄養成分の抽出
    product_list = []
    for url in sejs_url:
        product_list.append(fetch_and_parse(domain + url))
    
    # カラム抽出
    values = next(iter(product_list[0].values()))
    nutrient_col = list(values.keys())
    
    # CSVファイル作成
    with open(config.SEVEN, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['商品名'] + nutrient_col)
        writer.writeheader()
        
        for product_item in product_list:
            for product_name, nutrition_data in product_item.items():
                row = {'商品名': product_name}
                row.update(nutrition_data)
                writer.writerow(row)
    return 0

if __name__ == '__main__':
    sej_url = 'https://www.sej.co.jp/products/a/cat/060010010000000/kanto/1/l100/'
    fetch_seven_eleven_products(sej_url)