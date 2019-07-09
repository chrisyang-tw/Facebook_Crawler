# 利用 Python + Selenium 製作 Facebook 粉絲專頁爬文程式

## 1. 前言

本程式能擷取 Facebook 各粉絲專頁上的貼文，同時擷取文章的內文、按讚、留言數等，並匯出成 Excel 檔中。若該貼文含有單張的圖片，也能一併將圖片儲存下來。可做為監測網路聲量的工具。

## 2. 程式操作與程式碼

### Step 1: 檔案確認

確認資料夾中的 "chromedriver.exe" 存在，此檔案是為了啟動虛擬瀏覽器。

### Step 2: 打開程式並依畫面指示操作

首先輸入臉書帳號密碼，這兩個變數只會讓程式進行一次性記憶，關閉程式後即會自動消失，故可放心使用。

```python
username = input('>> 請輸入您的帳號，輸入完成按下 enter 鍵：')
password = input('>> 請輸入您的密碼，輸入完成按下 enter 鍵：')
```

接下來就必須輸入欲擷取的粉專貼文網址。以 ASUS TW 粉絲專頁為例，粉專貼文網址並不是 "https://www.facebook.com/asusclub.tw/" *(如圖一)*，請在粉絲專頁側邊選擇「貼文」頁籤，此時網址列當中的網址 "https://www.facebook.com/pg/asusclub.tw/posts/?ref=page_internal" 才是粉專貼文網址。*(如圖二)*

圖一：此網址並非貼文網址，請點擊左側的「貼文」。
![ptt_index](/md_img/page.jpg)

圖二：點擊後的網址才是貼文網址，用此網址去做擷取的動作較不易有誤。
![ptt_index](/md_img/page01.jpg)

此處製作了簡易的防呆機制。

```python
while True:
    temp_input = input('\n>> 請輸入粉專貼文網址，不再輸入請按大寫 N 並按下 enter 鍵 (開頭是 \'https://www.facebook.com/...\')：')
    if (temp_input != 'N') and ('https://www.facebook.com/' in temp_input):
        page_list.append(temp_input)
    elif temp_input == 'N':
        break
    else:
        print('您似乎輸入了非網址，請檢查後重新輸入！\n')

```
接著請輸入要取得過去幾天內的文章，例如輸入 "14"，程式即會將從現在算起過去兩周的所有文章擷取下來。

### Step 3: 開始爬蟲

在以上步驟接設定完成後將會開始執行爬蟲。此時程式會自動開啟一個 Chrome 瀏覽器視窗，若是第一次使用，可能會跳出防火牆訊息，此為正常現象，請將其關閉或接受（拒絕亦可）。另外，主程式上將會顯示擷取的進度，若不確定程式是否有在運作，可以前往主程式上查看。

**注意!!!當成功開啟第一個粉絲專頁時，Facebook 會跳出訊息「要求下列
權限：顯示通知」，請務必手動將其封鎖，否則程式無法執行。**

此處的程式碼較為複雜，將在第三部分敘述。

### Step 4: 執行完畢

爬蟲完畢後，瀏覽器將會關閉，此時將會發現與程式相同的資料夾中會出現方才所有粉專上的所有貼文圖片，以及一個 CSV 檔案，由於 Facebook 編碼與 Excel 不同，**請不要直接使用 Excel 打開**，請參照下方說明。

請先使用 Excel 打開一個空白的活頁簿，並點擊上方的「資料」標籤中的「從文字/CSV」。
![ptt_index](/md_img/excel.jpg)

接著在檔案選取視窗選取剛剛爬下來的檔案後，應會出現類似下圖的窗格，我們可以發現儲存格都是亂碼。點擊「檔案原點」的選取欄位。
![ptt_index](/md_img/excel01.jpg)

找到「65001: Unicode (UTF-8)」，並按下「載入」，即可順利載入剛剛擷取的資料。最後另存新檔就大功告成了。
![ptt_index](/md_img/excel02.jpg)

完成此步驟後，即可開始利用 Excel 的排序與篩選功能，挑選出想要的文章，或觀察各粉絲專頁的討論熱門程度。

## 3. 爬蟲程式碼詳述

首先，開啟一個空白的虛擬瀏覽器並進入 Facebook 網站。隨後，找到帳號欄和密碼欄的 id 來填入帳號密碼值，再找到登入按鈕並點擊。

```python
driver = webdriver.Chrome('./chromedriver.exe')
driver.get('https://www.facebook.com')
driver.find_element_by_id('email').send_keys(username)
driver.find_element_by_id('pass').send_keys(password)
driver.find_element_by_id('loginbutton').click()
```

在進入至第一個使用者欲爬取的粉絲專頁後，因為權限要求頁面會使視窗無法捲動，故程式會先暫停，待使用者手動關閉並按下 enter 鍵後才會繼續動作。

```python
while brand_index == 0:
    temp_msg = input('請先關閉或封鎖通知權限的視窗！關閉後再按 enter 繼續...')
    if temp_msg == '':
        break
```

頁面在每次捲動時，我會給予 5 秒鐘的休息時間，為的是讓頁面能順利生成載入。此處的值可以依網路狀態和頁面載入速度做調整，並不一定要是 5 秒鐘。至於捲動，我使用的是 javascript 語法 *window.scrollTo* 來實現。

```python
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
time.sleep(5)
```

在每次新頁面載入後，程式首先會判斷該頁最後一則貼文的日期是否有超過日期範圍，未超過則會往下捲動頁面，若超過就會進入下一階段的元件擷取與輸出。（程式碼略）

最後是貼文圖片下載的部分。若該篇貼文僅有一張圖片，該圖的 id 會是相同的，故取得圖片的 html 碼後，使用 *request.get* 將照片取下，再使用 ``` f.write(r._content)``` 將其下載下來。

```python
print('完成 %s 粉專第 %d 篇貼文的爬取！'%(brand, post_index))
try:
    img_link = i.find('a', '_50z9').get('data-ploi')
    r = requests.get(img_link)
    with open('%s_post_%d.png'%(brand, post_index), 'wb') as f:
        f.write(r._content)
except:
    print('查無圖片！')
```

## 4. 目前遇到的困難與常見問題

### 為何有些貼文的圖片在資料夾中找不到？

Ans: 設計的程式中僅會將只有單一圖片的貼文圖片下載下來，若該篇貼文有超過一張圖片，由於網頁程式碼稍有不同，所有圖片皆不會被下載。

### 為何有幾篇貼文的內文與按讚數顯示空白，且留言 + 分享顯示 0？

Ans: 可能代表該篇文章為網誌類型文章，由於該類型的網頁程式碼與一般貼文不同，這類型文章無法進行擷取。網誌類型文章通常也較不重要，故可放心忽略。

### 粉專一篇貼文都沒有擷取下來，且我確定粉專網址、日期皆沒有輸入錯誤，怎麼回事？

Ans: 可以觀察該粉專的置頂貼文的日期是否在擷取區間(取得幾天內的文章)外？由於目前程式無法忽略置頂貼文，故在發現置頂貼文的日期超過日期區間後，將直接結束執行。建議的解決辦法是將日期區間拉長，再自行將非觀測期間的貼文刪除。