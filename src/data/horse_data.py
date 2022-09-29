import time

from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
from tqdm import tqdm


# urlの末尾が年月日にちになっていることを利用する
# そのためにカレンダーから土日の日付を持ってくる
# 2010年から2022年の土日の日付を文字列型で取得
def create_holiday_list():
    holiday_list = []

    def get_holiday(year):
        base_date = datetime.date(int(year), 1, 1)
        days = (base_date - datetime.date(int(year) - 1, 1, 1)).days
        for i in range(0, days):
            if (base_date + datetime.timedelta(i)).weekday() >= 5:
                holiday_list.append(str(base_date + datetime.timedelta(i)))

    for i in range(2011, 2012, 1):
        get_holiday(i)
    return holiday_list


# 取得した日付をurlに追加することで全urlを作成する。
# URLのリストを返却する。
def create_url(holiday_list):
    url_list = []
    for holiday in holiday_list:
        url = "https://db.netkeiba.com/race/list/"
        # 以下で余分なハイフンを取り除く
        add_date = holiday.replace("-", "")
        # ここで日付と日時を紐つける
        url += add_date
        url_list.append(url)
    return url_list


# url = 'https://db.netkeiba.com/race/list/20100605/'
# 辞書型で日にちとデータを紐づけたい
def get_horse_data(url_list):
    format_url = "https://db.netkeiba.com"
    race_result = dict()
    for url in tqdm(url_list):
        res = requests.get(url)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, features="lxml")
        cls = soup.find_all(class_='race_top_data_info fc')
        # linkをそれぞれ取得していく
        for link in cls:
            next_page = format_url + link.find("a").get("href")
            # 次のリンク先がわかったので、そのままジャンプ,timeを用いてサーバー負荷を減らす
            next_res = requests.get(next_page)
            race_result[next_page] = pd.read_html(next_page)[0]
            print(next_page)
            time.sleep(1)
    return race_result


def create_data():
    new_list = create_holiday_list()
    new_url_list = create_url(new_list)
    print(get_horse_data(new_url_list))


create_data()
