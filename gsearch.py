from google.colab import auth
auth.authenticate_user()

import gspread
from oauth2client.client import GoogleCredentials

gc = gspread.authorize(GoogleCredentials.get_application_default())

import sys
import requests
import bs4
import urllib.parse
import datetime

def replace_n(str_data):
    return str_data.replace('\n', '').replace('\r', '')

def concat_list(list_data):
    str_data = ''
    for j in range(len(list_data)):
        str_data = str_data + replace_n(list_data[j].getText()).strip() + '\n'
    return str_data.rstrip("\n")

output_data = []

columns = ['検索順位', 'url', 'titleタグ', '記事文字数']
output_data.append(columns)

#''内の文字が検索ワードとなります。
list_keyword = ['ベストケンコー　クーポン']


if list_keyword:
    #num=10の数字を変更することで、抽出する検索結果数を変更できます。
    search_url = 'https://www.google.co.jp/search?hl=ja&num=10&q=' + '　'.join(list_keyword)
    res_google = requests.get(search_url)
    res_google.raise_for_status()

    bs4_google = bs4.BeautifulSoup(res_google.text, 'html.parser')

    link_google = bs4_google.select('.kCrYT > a') #Googleの仕様変更により修正が必要な場合がある

    for i in range(len(link_google)):

        site_url = link_google[i].get('href').split('&sa=U&')[0].replace('/url?q=', '')

        site_url = urllib.parse.unquote(urllib.parse.unquote(site_url))

        if 'https://' in site_url or 'http://' in site_url:

            try:
                res_site = requests.get(site_url)
                res_site.encoding = 'utf-8'
            except:
              continue
            bs4_site = bs4.BeautifulSoup(res_site.text, 'html.parser')



            title_site = ''



            if bs4_site.select('title'):
                title_site = replace_n(bs4_site.select('title')[0].getText())

            if bs4_site.select('body'):
                mojisu_site = len(bs4_site.select('body')[0].getText())


            output_data_new = i+1, site_url, title_site,  mojisu_site
            output_data.append(output_data_new)


table_data = output_data

row_len = len(table_data)
col_len = len(table_data[0])

now = datetime.datetime.now()
mojiretsu = ' '.join(list_keyword)
sheet_name = '[' + mojiretsu + ']' + '{0:%Y%m%d%H%M%S}'.format(now)

sh = gc.create(sheet_name)
worksheet = gc.open(sheet_name).sheet1


worksheet.add_rows(row_len)

# 出力先の指定はA1形式だけでなくセルの行と列番号でも指定できます。
cell_list = worksheet.range(1, 1, row_len, col_len)
col_list = [flatten for inner in table_data for flatten in inner]

for cell, col in zip(cell_list, col_list):
  cell.value = col

worksheet.update_cells(cell_list)
#command+returnで実行→リンクをクリック→アカウントを選択→パスコード取得→下記にボックスに貼り付け→return
