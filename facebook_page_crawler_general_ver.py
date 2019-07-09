# 抓取 Facebook 各品牌粉專上的文章（幾天前的文章）
# Version 1.3: 自定義粉專

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time, re
import csv
import datetime as dt
import requests

#####################################
## 前置作業、變數定義
page_list = list()

print('====================================\n歡迎使用 Facebook 粉絲專頁爬文程式！\n====================================\n')

print('請先輸入您的 Facebook 帳號密碼，此僅會作為一次性使用，程式並不會記憶或回傳至其他地方，請放心使用！')
username = input('>> 請輸入您的帳號，輸入完成按下 enter 鍵：')
password = input('>> 請輸入您的密碼，輸入完成按下 enter 鍵：')

username = 'b04303051@g.ntu.edu.tw'
password = 'Angelina01'

while True:
    temp_input = input('\n>> 請輸入粉專貼文網址，不再輸入請按大寫 N 並按下 enter 鍵 (開頭是 \'https://www.facebook.com/...\')：')
    if (temp_input != 'N') and ('https://www.facebook.com/' in temp_input):
        page_list.append(temp_input)
    elif temp_input == 'N':
        break
    else:
        print('您似乎輸入了非網址，請檢查後重新輸入！\n')

while True:
    try:
        dt_num = int(input('\n>> 請輸入要取得幾天以內的文章，並按下 enter 鍵 (ex:7)：'))
        break
    except ValueError:
        print('您輸入了非數值之字元，請重新輸入數字代碼！')

end_date = dt.datetime.today().date()
start_date = end_date - dt.timedelta(days = dt_num - 1)

#####################################
## 瀏覽器開啟、爬蟲開始
print('即將取得近 %d 天的貼文，欲取得的粉專共有 %d 個'%(dt_num, len(page_list)))
print('\n>> 請注意，程式執行完畢後會自動關閉 Chrome 瀏覽器，請勿手動關閉以免程式錯誤。\n若出現防火牆訊息，可點選關閉或接受。')
input('---請按下 Enter 鍵以開始爬蟲---')

csv = open('Facebook 粉專爬文_%s.csv'%end_date.strftime('%m%d'), 'w', encoding='utf8')
csv.write('粉專名稱,編號,日期時間,內文,文章連結,按讚數,留言+分享數,\n')

print('>> 正在開啟瀏覽器...')
driver = webdriver.Chrome('./chromedriver.exe')
print('>> 開啟網頁中...')
driver.get('https://www.facebook.com')
print('>> 登入中...')
driver.find_element_by_id('email').send_keys(username)
driver.find_element_by_id('pass').send_keys(password)
driver.find_element_by_id('loginbutton').click()

brand = ''
brand_index = 0
for index in page_list:
    brand = index.split('/')[3]
    print('正在開啟網頁...')
    driver.get(index)

    while brand_index == 0:
        temp_msg = input('請先關閉或封鎖通知權限的視窗！關閉後再按 enter 繼續...')
        if temp_msg == '':
            break

    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(5)

    post_index = 0
    while True:
        ## 先判斷該頁最後一則貼文的日期是否有超過日期範圍，超過即輸出，未超過則往下捲動頁面
        for i in driver.find_elements_by_css_selector('div.userContentWrapper'):
            last_date_time = i.find_element_by_css_selector('a._5pcq abbr').get_attribute('title')
        last_date_time = dt.datetime.strptime(last_date_time.split()[0], '%Y/%m/%d').date()
        if last_date_time < start_date:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            for i in soup.find_all('div', '_5pcr userContentWrapper'):
                date = content = link = ''
                post_index += 1
                date = i.find('a', '_5pcq').find('abbr').get('title')
                date_dt = dt.datetime.strptime(date.split()[0], '%Y/%m/%d').date()

                ## 判斷該則貼文是否在日期範圍內
                if date_dt >= start_date:
                    ## 寫入 csv：日期，內文，連結，讚數，留言+分享數
                    try:
                        content = i.find('div', '_5pbx').find('p').getText()
                        content = content.replace(',', '，')
                        link = 'https://www.facebook.com' + i.find('a', '_5pcq').get('href')
                        link = link.split('?__xts__')[0].split('?type=3')[0]
                        like = i.select('span._3dlg span._3dlh')[0].getText().replace(',', '')
                        if '萬' in like:
                            like = str(eval(like.replace('\xa0萬', ''))*10000)
                        comment_share = i.select('div._4vn1')
                    except:
                        like = ''
                        comment_share = []
                    if comment_share != []:
                        comment_share = comment_share[0].getText().replace('則留言', ' ').replace('次分享', ' ').replace('萬次觀看', '').replace('次觀看', '').replace(',', '')
                        c_list = comment_share.split()
                    else:
                        c_list = []
                    if len(c_list) == 3:
                        c_list = c_list[:-1]
                    num = 0
                    for j in range(len(c_list)):
                        num += eval(c_list[j])
                    csv.write(brand + ',' + str(post_index) + ',' + date + ',' + content + ',' + link + ',' + like + ',' + str(num) + ',\n')
                    brand_index += 1

                    ## 貼文圖片下載
                    print('完成 %s 粉專第 %d 篇貼文的爬取！'%(brand, post_index))
                    try:
                        img_link = i.find('a', '_50z9').get('data-ploi')
                        r = requests.get(img_link)
                        with open('%s_post_%d.png'%(brand, post_index), 'wb') as f:
                            f.write(r._content)
                    except:
                        print('查無圖片！')
            break
        else:
            ## 滾動至最底
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(5)
    print('完成 %s 粉專的爬文！'%brand)

print('>> 正在關閉瀏覽器...')
driver.close()
print('>> 完成！')

print('\n>> CSV 檔案與貼文圖片已儲存在與程式相同的資料夾中！執行完畢！\n>> CSV 檔請勿直接使用 Excel 開啟，請使用匯入功能，謝謝！')
csv.close()

#####################################
## 寫成 exe 檔
## pyinstaller -F D:\OneDrive\ASUS_INTERN\facebook_page_crawler_1.5.py