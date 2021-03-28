from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
from urllib import parse
import pandas as pd
import time
import requests



def getData(url):
    request_url = 'https:'+str(url).strip()
    res = requests.get(request_url)

    info = ''           # 出租者
    info_identity = ''  # 出租者身份
    phone = ''          # 連絡電話
    room_type = ''      # 型態
    status = ''         # 現況
    sex = ''            # 性別要求
    addr = ''           # 地址

    # 200 OK: success state respone
    if res.status_code == 200:
        bs = BeautifulSoup(res.text,'html.parser')

        addr = bs.find('span',{'class':'addr'}).text
        room_attribute = bs.find('ul',{'class':'attr'}).findAll('li')
        info = str(bs.find('div', {'class':'avatarRight'}).findAll())
        phone = str(bs.find('span', {'class':'dialPhoneNum'}))

        # get information of 'room_tpye' and 'status'
        if room_attribute:
            for attr in room_attribute:
                if attr.text.split('\xa0:\xa0\xa0')[0]=='型態':
                    room_type = attr.text.split('\xa0:\xa0\xa0')[1]
                elif attr.text.split('\xa0:\xa0\xa0')[0]=='現況':
                    status = attr.text.split('\xa0:\xa0\xa0')[1]

        # get information of 'sex'
        room_descriptions = bs.find('ul',{'class':'labelList-1'}).findAll('li')
        if room_descriptions:
            for description in room_descriptions:
                if description.text.split('：')[0]=='性別要求':
                    sex = description.text.split('：')[1]
                    if(sex.find('男女生') != -1):
                        sex = str('男女生皆可')
                    elif(sex.find('女生') != -1):
                        sex = str('女生')
                    else:
                        sex = str('男生')

        # get information of 'info'
        index_s = info.find('<i>')
        index_e = info.find('</i>')
        renter = info[index_s + 3:index_e]

        # get information of 'info_identity'
        identity_s = info.find('</i>')
        identity_e = info.find('</div>')
        if(info[identity_s + 5 : identity_e - 1].find('屋主') != -1):
            info_identity = str('屋主')
        elif(info[identity_s + 5 : identity_e - 1].find('代理人') != -1):
            info_identity = str('代理人')
        else:
            info_identity = str('仲介')

        # get information of 'phone'
        if phone:
            try:
                phone = phone.split('"')[3]
            except IndexError:
                phone = ''

        return str(renter), str(info_identity), phone, room_type, status, sex, addr
    else:
        return renter, info_identity, phone, room_type, status, sex, addr


def writeToCSV(house_detail, csvName):
    columns_name = ['info', 'info_identity', 'phone', 'room_type', 'status', 'sex', 'addr']
    house_db = pd.DataFrame()
    
    house_db = house_db.append(pd.DataFrame(house_detail, columns=columns_name), ignore_index=True)
    print('CSV size:'  + str(house_db.shape))
    house_db.to_csv(csvName, encoding='utf_8_sig', index=False)


def writeToMongo(house_detail):
    # MongoDB Client Server setting
    user = parse.quote_plus("KuanJu")
    passwd = parse.quote_plus("d8@UHtNqBUkrScE")
    # client = MongoClient("mongodb+srv://{0}:{1}@cluster0.kplej.mongodb.net/HouseDB?retryWrites=true&w=majority".format(user, passwd))

    client = MongoClient()                      # MongoDB: Client of LocalHost
    database = client["HouseDB"]                # MongoDB: Database Name
    collection = database["HouseCollection"]    # MongoDB: Table Name
    
    columns_name = ['info', 'info_identity', 'phone', 'room_type', 'status', 'sex', 'addr']
    house_db = pd.DataFrame()
    house_db = house_db.append(pd.DataFrame(house_detail, columns=columns_name), ignore_index=True)
    print('MongoDB size:'  + str(house_db.shape))
    records = house_db.to_dict(orient="records")
    collection.insert_many(records)


def webVisiting(browser):
    bs = BeautifulSoup(browser.page_source, 'html.parser')
    totalpages = int(int(bs.find('span', {'class':'TotalRecord'}).text.split(' ')[-2])/30 + 1)  # get totalpages from website
    print('Total pages: ', totalpages)


    house_list = []
    for i in range(totalpages):
        room_url_list=[] 
        bs = BeautifulSoup(browser.page_source, 'html.parser')  # got website page information

        titles = bs.findAll('h3')
        for title in titles:
            room_url = title.find('a').get('href')
            room_url_list.append(room_url)

        for url in room_url_list:
            renter, info_identity, phone, room_type, status, sex, addr = getData(url)   # return rent house details
            # check if house detail is NULL
            if renter != '':
                house_list.append([renter, str(info_identity), phone, room_type, status, sex, addr])
            print(house_list[len(house_list) - 1])
        print('Percentage: ' + str(int(i/totalpages*100)) + '%, Page: ' + str(i + 1))

        if i == (totalpages - 1):
            pass
        else:
            browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE)
            browser.find_element_by_class_name('pageNext').click()
    
    print('house detail get done...')
    return house_list

def main():
    house_detailList = []
    url = "https://rent.591.com.tw/?kind=0&region=1"                        # 591租屋網 URL
    browser = webdriver.Chrome(executable_path=r'D:\chromedriver.exe')

    browser.get(url)
    browser.find_element_by_id('area-box-close').click()                    # cloase the area-select box
    time.sleep(3)
    browser.find_element_by_class_name('pageNext').send_keys(Keys.ESCAPE)   # ECS key
    time.sleep(3)

    # get taipei city house renting information
    house_detailList.extend(webVisiting(browser))
    writeToMongo(house_detailList)
    writeToCSV(house_detailList, '台北HouseDB.csv')
    house_detailList.clear()

    # change dict to new taipei city and reload
    browser.delete_cookie("urlJumpIp")
    browser.add_cookie({'name':'urlJumpIp', 'value': '3'})
    browser.refresh()

    browser.get(url)
    time.sleep(3)

    # get new taipei city house renting information
    house_detailList.extend(webVisiting(browser))
    writeToMongo(house_detailList)
    writeToCSV(house_detailList, '新北HouseDB.csv')
    house_detailList.clear()
    

main()