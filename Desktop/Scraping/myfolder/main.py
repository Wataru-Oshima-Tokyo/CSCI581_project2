from datetime import datetime
from time import sleep
import re
import csv
import pandas as pd
import math 
from threading import Thread
# import decisionMaking

# decisionMaking
from selenium import webdriver
import lxml
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import psycopg2
import smtplib
from email.mime.text import MIMEText


# class sendEmailtoTheUser:

# メッセージの作成
def create_message(from_addr, to_addr, subject, body_txt):
    msg = MIMEText(body_txt)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    return msg

# メールの送信
def send_mail(msg, myadd, mypass):
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(myadd, mypass)
        server.send_message(msg)

def main(rateofwintext, titletext):
    my_addr = "wataru.pokemon.go.0722@gmail.com"
    my_pass = "oqficpdltqyrxklr"
    now = datetime.now()
    todays_date = str(now.strftime("%Y年%m月%d日%H:%M:%S ")) 
    title = todays_date + str(titletext)
    showResult = rateofwintext
    if showResult:
        msg = create_message(my_addr, my_addr, title, showResult)
        send_mail(msg, my_addr, my_pass)
        print("successfully emailed to the user")


def get_connection():
    return psycopg2.connect(
        host="ec2-54-145-249-177.compute-1.amazonaws.com",
        database="de9plpmh2fjj3f",
        user="xwhjswdrcuymes",
        password="2d6ceea971ed2e71ec3aa82f7b9fa570ff3f697fc57bea8e9c899877befe4d7a",
        port="5432")

def reportThePCC(content):
    title = "PCC"
    main(content, title)

def readDatafromdataDB():
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    # df = pd.read_sql('SELECT * FROM data', conn)
    cur.execute('SELECT * FROM data')
    content =""
    for row in cur:
        if (str(row[1]) == todays_date):
            content = content + "Time: "+ str(row[2]) +" PCC in 60 minutes: " +str(row[3]) +"\n"
        else:
            pass
    # try:
    #     # df.to_csv('/Users/wataruoshima/Desktop/Scraping/daytradedemowithDB/' + 'data' + ".csv", encoding='utf_8_sig')
    #     print("successfully emailed to the user")
    # except:
    #     print("failed to convert to csv file")
    reportThePCC(content)
    # cur.execute('SELECT * FROM data')
    # print(cur.fetchall())
    cur.close()
    conn.close()

def readDatafromresultDB():
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    df = pd.read_sql('SELECT * FROM percent', conn)
    try:
        # df.to_csv('/Users/wataruoshima/Desktop/Scraping/daytradedemowithDB/' + 'result' + ".csv", encoding='utf_8_sig')
        print("successfully converted to csv file")
    except:
        print("failed to convert to csv file")

    cur.close()
    conn.close()

def readDataExcuting():
    readDatafromdataDB()
    readDatafromresultDB()

def readDatafromresultDBandShowTheRateOfWin():
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    cur.execute('SELECT * FROM percent')
    totalWin =0
    toalGame = 0
    for row in cur:
        win =0
        draw = 99999
        try:
            win = float(row[3])
        except:
            win = -1
        try:
            draw = float(row[5])
        except:
            pass
        if (win >= 0.0):
            totalWin +=1
            toalGame +=1
        elif (draw == 0):
            pass
        else:
            toalGame +=1
    rateOfWin = (totalWin/toalGame)*100
    msg = "So far you have tried " + str(toalGame) + " times and won " +str(totalWin) +" times.\nSo your rate of win is " + str(rateOfWin) + "%."
    print(msg)
    # try:
    #     df.to_csv('/Users/wataruoshima/Desktop/Scraping/daytradedemowithDB/' + 'result' + ".csv", encoding='utf_8_sig')
    #     print("successfully converted to csv file")
    # except:
    #       print("failed to convert to csv file")
    cur.close()
    conn.close()
    return msg

def writeResult(rate, now, todays_date):
    #日付を取得
    current_time = 'h' + now.strftime("%H")
    # result.dbを作成する
    # すでに存在していれば、それにアスセスする。
    conn = get_connection()
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()
    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    try:
        cur.execute('CREATE TABLE percent(id SERIAL NOT NULL, date text, time text, win text, lose text, draw text, PRIMARY KEY (id))')
    except:
        conn.rollback()
        pass
    #日付を入れる
    # "PCC"に"pcc(引数）"を入れる
    if(rate >0):
        try:
            cur.execute('INSERT INTO percent(date, time, win) VALUES(%s,%s,%s)',(todays_date,current_time,rate))
        except:
            conn.rollback()
        pass
    elif(rate<0):
        try:
            cur.execute('INSERT INTO percent(date, time, lose) VALUES(%s,%s,%s)',(todays_date,current_time,rate))
        except:
            conn.rollback()
        pass
    else:
        try:
            cur.execute('INSERT INTO percent(date, time, draw) VALUES(%s,%s,%s)',(todays_date,current_time,rate))
        except:
            conn.rollback()
        pass
    #いらない欄を消す
    # sql = 'DELETE FROM data WHERE id=?'
    # データベースへコミット。これで変更が反映される。  
    conn.commit()
    cur.execute('SELECT * FROM percent')
    print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

def createAndWriteDB(pcc):
    #日付を取得
    pcc =str(pcc)
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    # 日付data.dbを作成する
    # すでに存在していれば、それにアスセスする。
    current_time = 'h' + now.strftime("%H")
    conn = get_connection()
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()
    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    try:
        cur.execute('CREATE TABLE data(id SERIAL NOT NULL, date text, time text, PCC60min text, PRIMARY KEY (id));')
    except:
        conn.rollback()
        pass
    #日付を入れる
    # "PCC"に"pcc(引数）"を入れる
    try:
        # cur.execute('ALTER TABLE data')
        postgres_insert_query = "INSERT INTO data(date, time, PCC60min) VALUES(%s,%s,%s)"
        record_to_insert = (todays_date, current_time, pcc)
        cur.execute(postgres_insert_query, record_to_insert)
        print("success to insert info into data")
        conn.commit()
    except:
        print(cur.query)
        print("failed to insert info into data")
    #いらない欄を消す
    # sql = 'DELETE FROM data WHERE id=?'
    # データベースへコミット。これで変更が反映される。  
    
    cur.execute('SELECT * FROM data')
    print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

def readDataForInverse(targethour):
    overallPcc = 0
    if (targethour == "h14"):
        now = datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 10
        for row in cur:
            if (row[1] == todays_date):
                if (start <=13):
                    total = "h" + str(start)
                    start +=1
                    if (row[2] ==total):
                        print(row[3])
                        overallPcc = str(row[3])
                        try:
                            overallPcc += float(overallPcc)
                            print("conversion sucess!!")
                        except:
                            overallPcc = 0 
                            break 
                    else:
                        break
                else:
                    break
            else:
                pass
        cur.close()
        conn.close()
        overallPcc = -1*(overallPcc/5)
        print(overallPcc)
        return overallPcc   
    elif (targethour=="h21"):
        now = datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 18
        while (start <= 21):
        #you can modify here h13 ->sth
            total = "h" + str(start)
            start +=1
            if (row[1] == todays_date):
                if (row[2] ==total):
                    overallPcc = str(row[3])
                    try:
                        overallPcc += float(overallPcc)
                        print("conversion sucess!!")
                    except:
                        overallPcc = 0 
                        break 
                else:
                    break
            else:
                pass
        overallPcc = -1*(overallPcc/4)
        cur.close()
        conn.close()
        return overallPcc   
    elif (targethour=="h01"):
        now = datetime.now()
        todays_date = int(now.strftime("%Y%m%d")) -1
        todays_date = str(todays_date)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 23
        while (start <= 25):
        #you can modify here h13 ->sth
            if (start >=24):
                total = "h" + str(start-24)
                now = datetime.now()
                todays_date = str(now.strftime("%Y%m%d")) 
            else:
                total = "h" + str(start)
            start +=1
            if (row[1] == todays_date):
                if (row[2] ==total):
                    overallPcc = str(row[3])
                    try:
                        overallPcc += float(overallPcc)
                        print("conversion sucess!!")
                    except:
                        overallPcc = 0 
                        break 
                else:
                    break
            else:
                pass
        overallPcc = -1*(overallPcc/3)
        cur.close()
        conn.close()
        return overallPcc
    else:
        pass 
def readData(targethour):
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    # df = pd.read_sql('SELECT * FROM data', conn)
    cur.execute('SELECT * FROM data')
    for row in cur:
        #you can modify here h13 ->sth
        if (row[2] ==targethour):
            pcc60min = str(row[3])
            try:
                pcc60min = float(pcc60min)
                msg = "conversion sucess!! : " + str(pcc60min)
                print(msg)
                break
            except:
                pcc60min = 0  
        else:
            pcc60min = 0  
    cur.close()
    conn.close()
    return pcc60min

def login(browser, un, pwd):
    browser.implicitly_wait(10)
    username_element = browser.find_element_by_id('accountId')
    username_element.send_keys(un)
    username_element = browser.find_element_by_id('password')
    username_element.send_keys(pwd)
    username_element = browser.find_element_by_id('LoginWindowBtn').click()
    browser.implicitly_wait(10)
    browser.implicitly_wait(10)
    window_after = browser.window_handles[1]
    browser.switch_to.window(window_after)
    sleep(5)
    # paegSource = browser.page_source

def controlBrowser(dm, targethour):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    url = 'https://demotrade.fx.dmm.com/fxcrichpresen/webrich/direct/login'
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    username = 'wataruoshima@my.smccd.edu'
    password = 'Ichiro0705'
    browser.get(url)
    print('ブラウザを起動しました')
    login(browser, username, password)
    print('ログインが完了しました')
    timeStart = 0
    if(dm==1):
        try:
            clickAsk = browser.find_element_by_xpath("//div[@uifield = 'askStreamingButton']").click()
            print("ASKを選択し、注文が完了しました")
        except:
            print("we cannot find ASK")
            enterAction = ActionChains(browser)
            tabAction = ActionChains(browser)
            tabAction.send_keys(Keys.RETURN)
            tabAction.perform()
            enterAction.perform()
            sleep(1)
            tabAction.perform()
            enterAction.perform()
            timeStart = 900
    elif (dm==-1):
        try:
            clickBid = browser.find_element_by_xpath("//div[@uifield = 'bidStreamingButton']").click()
            print("BIDを選択し、注文が完了しました")
        except:
            print("we cannot find BID")
            enterAction = ActionChains(browser)
            tabAction = ActionChains(browser)
            tabAction.send_keys(Keys.RETURN)
            tabAction.perform()
            enterAction.perform()
            sleep(1)
            tabAction.perform()
            enterAction.perform()
            timeStart = 900
    else :
        print("not buy/sell this time")
        timeStart = 900
    
    sleep(0.5)
    timetowait = 0
    if (targethour == "h14"):
        now = datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h21"):
        now = datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h01"):
        now = datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    else:
        timetowait =900

    while (timeStart <900):
        sleep(1)
        timeStart +=1
        searchpips = browser.find_element_by_xpath("//span[@uifield = 'evaluationPips']").text.strip()
        try:
            searchpips = float(searchpips)
        except:
            searchpips =0
        if (searchpips >= 10.0):
            break
        elif (searchpips <= -10.0):
            break
        else:
            continue
    try:
        clickclose = browser.find_element_by_xpath("//button[@uifield = 'quickCloseOrderButton']").click()
        actions = ActionChains(browser)
        nextaction = ActionChains(browser)
        nextaction.send_keys(Keys.RETURN)
        actions.send_keys(Keys.TAB)
        actions.perform()
        actions.perform()
        sleep(0.5)
        nextaction.perform()
        print("決済が完了しました")
    except:
        print("it is already closed")
    sleep(2)    
    browser.quit()
    return searchpips

def bidOrAsk(pcc, targethour):
    rateOfWin = 0
    # I guess that you can modify the percent here as you see the pcc
    if (pcc>0):
        pcc =1
        rateOfWin = controlBrowser(pcc, targethour)
    elif (pcc<0):
        pcc=-1
        rateOfWin = controlBrowser(pcc, targethour)
    else: 
        print("not buy anything")
        sleep(900)
    return rateOfWin

def mainexecuting(targethour, now, todays_date):
    # 実行   
    if (targethour =="h15"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h21"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h01"):
        pcc = readDataForInverse(targethour)
    else:
        pcc = readData(targethour)
    percent = bidOrAsk(pcc, targethour)
    writeResult(percent, now, todays_date)
    showResult = readDatafromresultDBandShowTheRateOfWin()
    title = "現在の勝率"
    main(showResult, title)


def extract():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
    url = 'https://info.finance.yahoo.co.jp/fx/detail/?code=usdjpy'
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def transform(soup,exr,ts,num):
    Rate = soup.find('dd', id = 'USDJPY_detail_bid').text.strip()
    try:
        RateInt =float(Rate)
        exr.append(RateInt)
        ts.append(num)
    except:
        num -= 1
        print("cannot convert from rateInt to int")
    return num
    

def pearsonCorrelationCoeffcient(classList):
    print("")
    x = classList.x
    y = classList.y
    xn = len(x)
    yn = len(y)
    xtotal = 0
    ytotal = 0
    for i in range(xn):
        xtotal +=x[i-1]
        ytotal +=y[i-1]
        xavg = xtotal/xn
        yavg = ytotal/yn
        numerator = 0
    for i in range(xn):
        xi = x[i-1]
        yi =y[i-1]
        numerator += (xi-xavg )*(yi-yavg)
        denominatorLeft =0
        denominatorRight =0
        denominator = 0
    for i in range(xn):
        xi = x[i-1]
        yi =y[i-1]
        denominatorLeft += (xi-xavg )*(xi-xavg )
        denominatorRight += (yi-xavg )*(yi-xavg )
        denominator = math.sqrt(denominatorLeft*denominatorRight)
    #     print("denominator is " +str(denominator))
    try:
        r = float (numerator/denominator)*100
        print("The pearson correlation coeffcient is " + str(r))
    except:
        r = 0
        print(r)
    return r

def job1():
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d"))
    exchangeRate =[]
    timeSpent =[]
    class elementList:
        x = exchangeRate
        y = timeSpent
    print("Gathering information", end="")
    target_date = int(now.strftime("%Y%m%d")) +1
    todays_dateInt =int(todays_date)
    i= int(now.strftime("%M"))*20
    overtime = i
    while (todays_dateInt != target_date):
        now = datetime.now()
        todays_dateInt =int(now.strftime("%Y%m%d"))
        i+=1
        c=extract()
        passedTime = i - overtime
        i = transform(c, exchangeRate, timeSpent, passedTime) + overtime
        print(i)
        if (i%1200==0):
            result = pearsonCorrelationCoeffcient(elementList)
            createAndWriteDB(result)
            readDatafromdataDB()
            i=0
            exchangeRate =[]
            timeSpent =[]
            now = datetime.now()
            current_time = int(now.strftime("%M"))
            elementList.x = exchangeRate
            elementList.y = timeSpent
            if(current_time > 40):
                timetowait = (60 -int(current_time))*60
                sleep(timetowait)
            elif(current_time <10):
                overtime = current_time*20
                i = overtime
        else:
            sleep(2.7)


def job2():
    todays_date ="0"
    while (todays_date != "20220219"):
        now = datetime.now()
        todays_date = str(now.strftime("%Y%m%d"))  
        #10時の東京市場順張りチェック
        current_time = int(now.strftime("%H%M%S"))
        if (current_time >= 100500):
            if(current_time <=110000):
                mainexecuting("h10", now, todays_date)
            elif(current_time <=120000):
                mainexecuting("h11", now, todays_date)
            elif(current_time <=130000):
                mainexecuting("h12", now, todays_date)
            elif(current_time <=134500):
                mainexecuting("h13", now, todays_date)
            else:
                pass
        else:
            pass
        #15時の東京市場逆張りチェック
        if (current_time >= 140500):
            if (current_time <= 142500):
                mainexecuting("h14", now, todays_date)
            else:
                pass
        else:
            pass       

        #18時のロンドン市場順張りチェック
        if (current_time >= 180500):
            if(current_time <=190000):
                mainexecuting("h18", now, todays_date)
            elif(current_time <=200000):
                mainexecuting("h19", now, todays_date)
            elif(current_time <=204500):
                mainexecuting("h20", now, todays_date)
            else:
                pass
        else:
            pass

        #21時のロンドン市場逆張りチェック
        if (current_time >= 210500):
            if (current_time <= 212500):
                mainexecuting("h21", now, todays_date)
            else:
                pass
        else:
            pass 
        # 25時のニューヨーク市場逆張りチェック
        if (current_time >= 500):
            if (current_time <= 1500):
                mainexecuting("h01", now, todays_date)
            else:
                pass
        else:
            pass 

        print(current_time)
        sleep(5)

# main = main()
# monitorExchangeRate = monitorExchangeRate()
# decisionMaking = decisionMaking()
# WriteDBAndReport = WriteDBAndReport()
# sendEmailtoTheUser = sendEmailtoTheUser()

job1 = Thread(target=job1)
job2 = Thread(target=job2)
job1.start()
job2.start()
