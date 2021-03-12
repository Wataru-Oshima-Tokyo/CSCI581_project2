from datetime import datetime
import datetime
from time import sleep
import re
import csv
import pandas as pd
import math 
from threading import Thread
import os
from fake_useragent import UserAgent

#まだメインにインポートしていない
import pytz
import oandapyV20.endpoints.instruments as instruments
# ------------------


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
from apscheduler.schedulers.blocking import BlockingScheduler
import json
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.trades as trades


# OANDA API
def getCandles():
    oneHourAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = 1.2)
    now = datetime.datetime.utcnow()
    winterOrSummer = int(now.strftime("%m%d"))
    date_from =""
    date_to =""
        
    API_access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"
    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    
    date_from = timeModified(oneHourAgo)
    date_to = timeModified(now)
    print("ターゲットタイム（UTC）は"+date_from + " to " + date_to)
    # <ろうそく足取得用URLの変数の設定>
    # /v3/instruments/{Account ID}/candles 
    for n in range(5):
        count = 720
        url = API_URL + "/v3/instruments/%s/candles?count=%s&price=M&granularity=S5&smooth=True&from=%s" % (INSTRUMENT, count,date_from)
        # ヘッダー情報の変数の設定
        headers = {
                        "Authorization" : "Bearer " + API_access_token
            }
        # サーバーへの要求
        response = requests.get(url, headers=headers)
        # 処理結果の編集
        Response_Body = response.json()
        # print(json.dumps(Response_Body, indent=2))
        i = 0
        pcc = []
        gatheringTime = []
        class ClassList:
            x = pcc
            y = gatheringTime
        while i<count:
            try:
                pcc5s = float(Response_Body["candles"][i]["mid"]["c"])
            except:
                break
            pcc.append(pcc5s)
            gatheringTime.append(i)
            i = i+1
        maximum = int(len(pcc))
        if(maximum > 0):
            break
        else:
            pass
    try:
        print(maximum)
        print("直前1分間のPCC")
        pcc1min = getEachPCC(ClassList, maximum, 12)
        print("直前5分間のPCC")
        pcc5min = getEachPCC(ClassList, maximum, 60)
        print("直前10分間のPCC")
        pcc10min =getEachPCC(ClassList, maximum, 120)
        print("直前30分間のPCC")
        pcc30min = getEachPCC(ClassList, maximum, 360)
        print("直前60分間のPCC")
        pcc60min = getEachPCC(ClassList, maximum,maximum)
        pcctotal = pcc1min*0.03 + pcc5min*0.07 + pcc10min*0.15 +pcc30min*0.25 + pcc60min*0.5
        pcctotal = str(pcctotal)
        print("I can conclude that the pcc during the period is " + pcctotal)
        print("The start price is " +Response_Body["candles"][0]["mid"]["o"] )
        print("The close price is " +Response_Body["candles"][maximum-1]["mid"]["o"] )
        return float(pcctotal)
    except:
        text = "You have an error for getting a pcc. This is probably due to the number of pcc we got which is most likely 0..."
        main(text, "errorcode=404: PCC not found")
        return 0
    

def getEachPCC(classList, maximumcount,target):
    x = classList.x
    y = classList.y
    tempList = []
    tempTime = []
    class temporaryList:
        x = tempList
        y = tempTime
    reverse = target
    for i in range(target):
        reverse =maximumcount -target+i
        tempList.append(x[reverse])
        tempTime.append(y[i])
    r = pearsonCorrelationCoeffcient(temporaryList)
    return r

def timeModified(date):
    date = str(date)
    choppedStr = date.split(" ")
    ChoppedStr2 = choppedStr[1].split(".")
    modifiedTime = choppedStr[0] +"T"+ChoppedStr2[0] + ".000000000Z"
    return modifiedTime


def executeBuyOrSell(pcc, targethour):
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    r = accounts.AccountSummary(accountID)
    acc = api.request(r)
    orderUnits = acc['account']['balance']

    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
        
    # 注文用URLの変数の設定 その１
    url = API_URL + "/v3/accounts/%s/orders" % str(accountID)
    
    # ヘッダー情報の変数の設定
    headers = {
                "Content-Type" : "application/json", 
                "Authorization" : "Bearer " + access_token
            }  
    
    # #データ情報の変数の設定
    try:
        orderUnits = float(orderUnits)
        orderUnits =math.floor(orderUnits)
    except:
        orderUnits = 1
    Order_units = orderUnits*5
    if (pcc<0):
        Order_units = -1* Order_units
        print("Bidで注文します")
    else:
        print("ASKで注文します")
    Pip_location = -2
    TP_pips = 10 #pips
    TP_distance = TP_pips * (10**Pip_location)
    SL_pips = 10 #pips
    SL_distance = SL_pips * (10**Pip_location)         
    
    data_Market = {
                    "order": {
                            "units": Order_units,
                            "instrument": "USD_JPY",
                            "timeInForce": "FOK",
                            "type": "MARKET",
                            "positionFill": "DEFAULT",
                            #SL
                            "stopLossOnFill" : {
                                    "distance": str(SL_distance),
                                    "timeInForce": "GTC" 
                                    },
                            }
                    }  
    
    data = json.dumps(data_Market)
        
    try:
        # サーバーへの要求
        Response_Body = requests.post(url, headers=headers, data=data)
        # エラー発生時に例外処理へ飛ばす
        Response_Body.raise_for_status()
                
        #約定されたトレード情報の取得
        #トレードID
        Trade_no = str(Response_Body.json()['orderFillTransaction']['tradeOpened']['tradeID'])
        #売買判定
        Trade_units = float(Response_Body.json()['orderFillTransaction']['tradeOpened']['units'])
        #約定価格
        Trade_price = float(Response_Body.json()['orderFillTransaction']['tradeOpened']['price'])

        #TPプライスの計算  
        if Trade_units > 0: 
                TP_price = Trade_price + TP_distance         
        else:
                TP_price = Trade_price - TP_distance         
        TP_price = round(TP_price, 3)  

        # トレード変更用URL変数の設定
        url = API_URL + "/v3/accounts/%s/trades/%s/orders" % (str(accountID), Trade_no)
            
        # データ情報の変数の設定
        data_Modify = {
                    #TP
                        "takeProfit" : {
                                "price": str(TP_price),
                                "timeInForce": "GTC"  
                                },
                        }

        data = json.dumps(data_Modify)
        Response_Body = requests.put(url, headers=headers, data=data)
        # エラー発生時に例外処理へ飛ばす
        Response_Body.raise_for_status()
            
        #結果の表示
        print("注文が確定しました")
        print(json.dumps(Response_Body.json(), indent=2))

    #例外処理
    except Exception as e:
            if "Response_Body" in locals(): # or vars()
                    print("Status Error from Server(raise) : %s" %Response_Body.text)
            
            print("エラーが発生しました。\nError(e) : %s" %e)
    
    timetowait = 0
    if (targethour == "h14"):
        now = datetime.datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h21"):
        now = datetime.datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h01"):
        now = datetime.datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
        timetowait += 10800
    else:
        timetowait =1500

    while(timetowait>1500):
        now = datetime.datetime.now()
        current_time = now.strftime("%H%M%S")
        print("We will determine the order after" + str(timetowait) + "s")
        sleep(600)
        timetowait -=600

    sleep(timetowait)

    # 指定時間後に自動決済
    try:
        r = trades.TradeClose(accountID ,tradeID=Trade_no)
        api.request(r)
        print("約定が確定しました")
    except:
        print("すでに約定しています")
    sleep(2)
    # 利益幅を確認する
    try:
        r = trades.TradeDetails(accountID ,tradeID=Trade_no)
        tradeDetail = api.request(r)
        tdr =tradeDetail["trade"]["realizedPL"]
    except:
        tdr = 0
    
    now = datetime.datetime.now()
    current_time = int(now.strftime("%M"))
    timptowait = 0
    if(current_time > 0):
        timetowait = (60 -int(current_time))*60
    else:
        timetowait = 3600
    print("I will wati for " + str(timetowait) +"s")
    while timetowait >600:
        timetowait -=600
        print("Market order function will be rebooted after" +str(timetowait) +"s.")
        sleep(600)
        now = datetime.datetime.now()
        current_time = int(now.strftime("%M"))
        if (current_time <= 10):
            timetowait = 0
            break
    sleep(timetowait)
    return tdr

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
    now = datetime.datetime.now()
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
    now = datetime.datetime.now()
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
    # print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

def createAndWriteDB(pcc):
    #日付を取得
    pcc =str(pcc)
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    # 日付data.dbを作成する
    # すでに存在していれば、それにアスセスする。
    # onehourAgo = int(now.strftime("%H"))-1
    # if onehourAgo <0:
    #     onehourAgo ="23"
    # current_time = 'h' +str(onehourAgo)+"to"+'h' + now.strftime("%H")
    current_time = "h" + now.strftime("%H")
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
    # print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

def createAndWriteDBex(pccList):
    #日付を取得
    pcc =str(pcc)
    now = datetime.datetime.now()
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
        cur.execute('CREATE TABLE data(id SERIAL NOT NULL, date text, time text, PCC1min text, PCC5min text, PCC10min text, PCC30min text, PCC60min text, PRIMARY KEY (id));')
    except:
        conn.rollback()
        pass
    #日付を入れる
    # "PCC"に"pcc(引数）"を入れる
    try:
        # cur.execute('ALTER TABLE data')
        postgres_insert_query = "INSERT INTO data(date, time, PCC1min, PCC5min, PCC10min, PCC30min, PCC60min) VALUES(%s, %s,%s,%s,%s,%s,%s)"
        record_to_insert = (todays_date, current_time, pccList[0],pccList[1],pccList[2],pccList[3],pccList[4])
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
    # print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

def readDataForInverse(targethour):
    overallPcc = 0
    eachPcc = 0
    if (targethour == "h14"):
        now = datetime.datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 10
        dividedby = 0
        for row in cur:
            if (row[1] == todays_date):
                total = "h" + str(start)
                if (row[2] ==total):
                    start +=1
                    dividedby +=1
                    try:
                        eachPcc = float(row[3])
                        print("conversion sucess!!")
                    except:
                        eachPcc =0
                    overallPcc += eachPcc
                else:
                    pass
            else:
                pass
        cur.close()
        conn.close()
        try:
            overallPcc = -1*(overallPcc/dividedby)
        except:
            overallPcc = 0
        print("The total pcc is from " + str(dividedby) + " hours ago to now is " +  str(overallPcc))
        return overallPcc   
    elif (targethour=="h21"):
        now = datetime.datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 18
        dividedby = 0
        for row in cur:
        #you can modify here h13 ->sth
            if (row[1] == todays_date):
                total = "h" + str(start)
                if (row[2] ==total):
                    start +=1
                    dividedby +=1
                    try:
                        eachPcc = float(row[3])
                        print("conversion sucess!!")
                    except:
                        eachPcc =0
                    overallPcc += eachPcc
                else:
                    pass
            else:
                pass
        try:
            overallPcc = -1*(overallPcc/dividedby)
        except:
            overallPcc = 0
        cur.close()
        conn.close()
        print("The total pcc is from " + str(dividedby) + " hours ago to now is " +  str(overallPcc))
        return overallPcc   
    elif (targethour=="h01"):
        now = datetime.datetime.now()
        todays_date = int(now.strftime("%Y%m%d")) -1
        todays_date = str(todays_date)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 23
        dividedby = 0
        for row in cur:
        #you can modify here h13 ->sth
            if (row[1] == todays_date):
                if (start >=24):
                    total = "h" + str(start-24)
                    now = datetime.datetime.now()
                    todays_date = str(now.strftime("%Y%m%d")) 
                else:
                    total = "h" + str(start)
                if (row[2] ==total):
                    start +=1
                    dividedby +=1
                    try:
                        eachPcc = float(row[3])
                    except:
                        eachPcc =0
                    overallPcc += eachPcc
                else:
                    pass
            else:
                pass
        try:
            overallPcc = -1*(overallPcc/dividedby)
        except:
            overallPcc = 0
        cur.close()
        conn.close()
        print("The total pcc is from " + str(dividedby) + " hours ago to now is " +  str(overallPcc))
        return overallPcc
    else:
        pass 

def readData(targethour):
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    # df = pd.read_sql('SELECT * FROM data', conn)
    cur.execute('SELECT * FROM data')
    for row in cur:
        if(todays_date == row[1]):
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
        else:
            pass  
    cur.close()
    conn.close()
    return pcc60min

def bidOrAsk(pcc, targethour):
    rateOfWin = 0
    pcc = float(pcc)
    # I guess that you can modify the percent here as you see the pcc
    if (pcc>0):
        pcc =1
        rateOfWin = float(executeBuyOrSell(pcc, targethour))
    elif (pcc<0):
        pcc=-1
        rateOfWin = float(executeBuyOrSell(pcc, targethour))
    else: 
        print("not buy anything")
        sleep(900)
    return rateOfWin

def mainexecuting(targethour, now, todays_date):
    # 実行   
    if (targethour =="h14"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h21"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h01"):
        pcc = readDataForInverse(targethour)
    else:
        pcc = readData(targethour)
    percent = bidOrAsk(pcc, targethour)
    if (percent !=0):
        writeResult(percent, now, todays_date)
        showResult = readDatafromresultDBandShowTheRateOfWin()
        title = "現在の勝率"
        main(showResult, title)

def pearsonCorrelationCoeffcient(classList):
    x = classList.x
    y = classList.y
    xn = len(x)
    yn = len(y)
    xtotal = 0
    ytotal = 0
    for i in range(xn-1):
        xtotal +=x[i]
        ytotal +=y[i]
    xavg = xtotal/xn
    yavg = ytotal/yn
    numerator = 0
    for i in range(xn-1):
        xi = x[i]
        yi =y[i]
        numerator += (xi-xavg )*(yi-yavg)
    denominatorLeft =0
    denominatorRight =0
    denominator = 0
    for i in range(xn-1):
        xi = x[i]
        yi =y[i]
        denominatorLeft += (xi-xavg )*(xi-xavg )
        denominatorRight += (yi-yavg )*(yi-yavg )
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
    now = datetime.datetime.now()
    todays_date = int(now.strftime("%Y%m%d")) 
    tommorow = todays_date +1
    while (todays_date != tommorow):  
        current_time = int(now.strftime("%M"))
        timptowait = 0
        if(current_time > 0):
            timetowait = (60 -int(current_time))*60
        else:
            timetowait = 3599
        pcc = getCandles()
        createAndWriteDB(pcc)
        readDatafromdataDB()
        print("I will wait for " + str(timetowait) +"s")
        while (timetowait >600):
            sleep(600)
            timetowait -=600
            print("We will take pcc again after " + str(timetowait) +"s")
            now = datetime.datetime.now()
        sleep(timetowait)
        now = datetime.datetime.now()
        todays_date = int(now.strftime("%Y%m%d"))

def job2():
    japanTime = datetime.datetime.now()
    newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
    todays_date = int(japanTime.strftime("%Y%m%d")) 
    tommorow = todays_date +1
    print(todays_date)
    print(tommorow)
    sleep(120)
    while (todays_date != tommorow):
        japanTime = datetime.datetime.now()
        tokyoTime = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
        newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
        todays_date = str(japanTime.strftime("%Y%m%d"))  
        current_timeJ = int(japanTime.strftime("%H%M%S"))
        #10時の東京市場順張りチェック
        if (tokyoTime.hour >= 10):
            if(tokyoTime.minute <=10):
                mainexecuting("h10", japanTime, todays_date)
                
            elif(tokyoTime.hour <=11):
                if(tokyoTime.minute <=10):
                    mainexecuting("h11", japanTime, todays_date)
                    
            elif(tokyoTime.hour <=12):
                if(tokyoTime.minute <=10):
                    mainexecuting("h12", japanTime, todays_date)
                    
            elif(tokyoTime.hour <=13):
                if(tokyoTime.minute <=10):
                    mainexecuting("h13", japanTime, todays_date)
                    
            else:
                pass
        else:
            pass
        #15時の東京市場逆張りチェック
        if (current_timeJ >= 140500):
            if (current_timeJ <= 141000):
                mainexecuting("h14", japanTime, todays_date)
            else:
                pass
        else:
            pass       
        
        #18時のロンドン市場順張りチェック
        if (londonTime.hour >= 10):
            if (londonTime.hour <= 10):
                if(londonTime.minute  <=20):
                    mainexecuting("h18", japanTime, todays_date)
            elif(londonTime.hour <=11):
                if(londonTime.minute <=10):
                    mainexecuting("h19", japanTime, todays_date)
            elif(londonTime.hour <=12):
                if (londonTime.minute <=10):
                    mainexecuting("h20", japanTime, todays_date)
            else:
                pass
        else:
            pass

        #21時のロンドン市場逆張りチェック
        if (londonTime.hour >= 13):
            if (londonTime.minute < 10):
                mainexecuting("h21", japanTime, todays_date)
            else:
                pass
        else:
            pass 
        

        #22時のニューヨーク市場順張りチェック
        if (newyorkTime.hour >= 9):
            if(newyorkTime.hour  <=10):
                if(newyorkTime.minute <=10):
                    mainexecuting("h22", japanTime, todays_date)
                    
            elif(newyorkTime.hour <=11):
                if(newyorkTime.minute <=10):
                    mainexecuting("h23", japanTime, todays_date)
                    
            elif(newyorkTime.hour <=12):
                if (newyorkTime.minute <=10):
                    mainexecuting("h24", japanTime, todays_date)
                    
            else:
                pass
        else:
            pass

        # 25時のニューヨーク市場逆張りチェック
        if (newyorkTime.hour >= 13):
            if (newyorkTime.minute < 10):
                mainexecuting("h01", japanTime, todays_date)
            else:
                pass
        else:
            pass 

        print(str(current_timeJ) +": Checking time for market order...")
        todays_date = int(japanTime.strftime("%Y%m%d")) 
        sleep(60)


# まだ本ファイルについかしていない
def job3():
    # 指値:逆指値注文用
    japanTime = datetime.datetime.now()
    newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
    todays_date = int(japanTime.strftime("%Y%m%d")) 
    tommorow = todays_date +1
    orderId = [] 
    timetowaitForsl =0
    flag =0
    while (todays_date != tommorow):
        japanTime = datetime.datetime.now()
        newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
        todays_date = str(japanTime.strftime("%Y%m%d"))  
        current_timeJ = int(japanTime.strftime("%H%M%S"))
        current_hour = int(japanTime.strftime("%H"))
        current_minute = int(japanTime.strftime("%M"))
         # 指値：逆指値を調べて１％以上注文が入っていたら注文を入れる(四時間ごとにチェック)
        if ((current_hour+2)%4 ==0):
            if (current_minute<2):
                timetowaitForsl = 0
                orderList = getShortAndLongCountPercent()
                stopLimitId = orderConfirmation(orderList)
                for i in stopLimitId:
                    orderId.append(i)
                timetowaitForsl = 14340
                sleep(60)
                flag = 1

        if (flag !=0):
            print("Stop or Limit function will be rebooted after " +str(timetowaitForsl) +"s")
            timetowaitForsl -=60
        else: 
            pass
        # 東京市場の高値：安値を調べて指値注文する
        if (londonTime.hour >= 9):
            if(londonTime.hour  <10):
                if(londonTime.minute  <=10):
                    eachId = subExecuting()
                    try:
                        orderId.append(eachId[0])
                    except:
                        orderId.append(0)
                    try:
                        orderId.append(eachId[1])
                    except:
                        orderId.append(0)

        print(str(current_timeJ) +": Cheking time for stop/limit order...")
        todays_date = int(japanTime.strftime("%Y%m%d")) 
        sleep(60)
    confirmResults(orderId, japanTime, todays_date)

    
def orderConfirmation(orderList):
    buyStop = orderList[0]
    buyLimit = orderList[1]
    sellStop = orderList[2]
    sellLimit = orderList[3]
    n=0
    for i in orderList:
        price = float(i)
        if (price > 0):
            n+=1
    tradeId =[]
    if(n!=0):
        percent = math.floor(10/n)
        if(buyStop != 0):
            resultId = orderFlexible(buyStop, "BUY", "STOP", percent)
            print("逆指値買いの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
        if(buyLimit != 0):
            resultId = orderFlexible(buyLimit, "BUY", "LIMIT", percent)
            print("指値買いの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
        if(sellStop != 0):
            resultId = orderFlexible(sellStop, "SELL", "STOP", percent)
            print("逆指値売りの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
        if(sellLimit != 0):
            resultId = orderFlexible(sellLimit, "SELL", "LIMIT", percent)
            print("指値売りの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
    return tradeId

def subExecuting():
    stopPrice = getCandlesForStopOredr()
    result = stopOrder(stopPrice)
    return result
    
def confirmResults(orderID, now, todays_date):
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    now = datetime.datetime.now()
    current_time = int(now.strftime("%M"))
    # 利益幅を確認する
    resultList=[]
    tradeIdList =[]
    for i in orderID:
        try:
            orderId = int(i)
            print(orderId)
            r = orders.OrderDetails( accountID ,orderID=orderId)
            CheckTradeId = api.request(r)
            tradeId = float(CheckTradeId['order']['tradeID'])
            resultList.apeend(tradeId)
        except:
            print('It was canceled')
            
    for i in tradeIdList:
        try:
            tr = orders.OrderDetails(accountID, tradeID=i)
            tradeDetail = api.request(tr)
            result = tradeDetail['trade']['realizedPL']
            resultList.append(result)
        except:
            pass
    for i in resultList:
            writeResult(i, now, todays_date)
    showResult = readDatafromresultDBandShowTheRateOfWin()
    title = "現在の勝率"
    main(showResult, title)
    
def stopOrder(limitPrice):
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    r = accounts.AccountSummary(accountID)
    acc = api.request(r)
    orderUnits = acc['account']['balance']

    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
        
    # 注文用URLの変数の設定 その１
    url = API_URL + "/v3/accounts/%s/orders" % str(accountID)
    
    # ヘッダー情報の変数の設定
    headers = {
                "Content-Type" : "application/json", 
                "Authorization" : "Bearer " + access_token
            }  
    
    # #データ情報の変数の設定
    try:
        orderUnits = float(orderUnits)
        orderUnits =math.floor(orderUnits)
    except:
        orderUnits = 1
    orderUnits = 100
    Order_unitsForAsk = orderUnits*5
    Order_unitsForBid = -1*orderUnits*5
    highestPriceinTokyo = limitPrice[0]
    lowestPriceinTokyo = limitPrice[1]
    print(highestPriceinTokyo)
    print(lowestPriceinTokyo)
    Pip_location = -2
    TP_pips = 10 #pips
    SL_pips = 10 #pips
    cancelTime = datetime.datetime.utcnow()+ datetime.timedelta(hours = 4)
    cancelTime = timeModified(cancelTime)
    print("canceltime should be " +str(cancelTime))
    Highest_TP_distance = round(highestPriceinTokyo + TP_pips * (10**Pip_location),3)
    Highest_SL_distance = round(highestPriceinTokyo - SL_pips * (10**Pip_location),3)
    Lowest_TP_distance = round(lowestPriceinTokyo - TP_pips * (10**Pip_location),3)
    Lowest_SL_distance = round(lowestPriceinTokyo + SL_pips * (10**Pip_location),3)        

    data_MarketHigh = {
                    "order": {
                            "units": str(Order_unitsForAsk),
                            "price": str(highestPriceinTokyo),
                            "instrument": "USD_JPY",
                            "timeInForce": "GTD",
                            "gtdTime":str(cancelTime),
                            "type": "STOP",
                            "positionFill": "DEFAULT",
                            #TP
                            "takeProfitOnFill" : {
                                "price": str(Highest_TP_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }, 
                            #SL
                            "stopLossOnFill" : {
                                "price": str(Highest_SL_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }
                               
                            }
                    }  

    data_MarketLow = {
                    "order": {
                            "units": str(Order_unitsForBid),
                            "price": str(lowestPriceinTokyo),
                            "instrument": "USD_JPY",
                            "timeInForce": "GTD",
                            "gtdTime":str(cancelTime),
                            "type": "STOP",
                            "positionFill": "DEFAULT",
                            #TP
                            "takeProfitOnFill" : {
                                "price": str(Lowest_TP_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }, 
                            #SL
                            "stopLossOnFill" : {
                                "price": str(Lowest_SL_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }   
                            }
                    }
    
    datahigh = json.dumps(data_MarketHigh)
    datalow = json.dumps(data_MarketLow)  
    try:
        # サーバーへの要求
        Response_BodyHigh = requests.post(url, headers=headers, data=datahigh)
        # エラー発生時に例外処理へ飛ばす
        Response_BodyHigh.raise_for_status()
        sleep(0.5)
        Response_BodyLow = requests.post(url, headers=headers, data=datalow)
        # エラー発生時に例外処理へ飛ばす
        Response_BodyLow.raise_for_status()  
        
        #結果の表示
        print("逆指値の注文が確定しました")
        orderIdList=[]
        idForHigh = json.dumps(Response_BodyHigh.json()['orderCreateTransaction']['id'])
        idForLow = json.dumps(Response_BodyLow.json()['orderCreateTransaction']['id'])
        print("オーダーIDは以下です")
        orderIdList.append(idForHigh)
        orderIdList.append(idForLow)
        print(orderIdList)
    #例外処理
    except Exception as e:
            if "Response_Body" in locals(): # or vars()
                    print("Status Error from Server(raise) : %s" %Response_Body.text)
            
            print("エラーが発生しました。\nError(e) : %s" %e)

    return orderIdList

def getCandlesForStopOredr():
    # I think I need to think of summer time and winter since this is started at 9 am in London
    bgOfTokyoMarket = datetime.datetime.utcnow()- datetime.timedelta(hours = 8)
    bgOfLondonMarket = datetime.datetime.utcnow()
    date_from =""
    date_to=""
        
    API_access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"
    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    
    date_from = timeModified(bgOfTokyoMarket)
    date_to = timeModified(bgOfLondonMarket)
    print("ターゲットタイム（UTC）は"+date_from + " to " + date_to)
    # <ろうそく足取得用URLの変数の設定>
    # /v3/instruments/{Account ID}/candles 
    count = 8
    url = API_URL + "/v3/instruments/%s/candles?count=%s&price=M&granularity=H1&smooth=True&from=%s" % (INSTRUMENT, count,date_from)
    # ヘッダー情報の変数の設定
    headers = {
                "Authorization" : "Bearer " + API_access_token
        }
    # サーバーへの要求
    response = requests.get(url, headers=headers)
    # 処理結果の編集
    Response_Body = response.json()
    # print(Response_Body)
    # print(json.dumps(Response_Body, indent=2))
    high =[]
    low =[]
    highestAndLowest =[]
    for i in range(count):
        high.append(float(Response_Body["candles"][i]["mid"]["h"]))
        low.append(float(Response_Body["candles"][i]["mid"]["l"]))
    high.sort()
    low.sort()
    highestAndLowest.append(high[count-1])
    highestAndLowest.append(low[0])
    # print(high)
    # print(low)
    # print(highestAndLowest)
    return highestAndLowest

def getShortAndLongCountPercent():
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    r = instruments.InstrumentsOrderBook(instrument="USD_JPY")
    m = instruments.InstrumentsPositionBook(instrument="USD_JPY")
    positionBook = api.request(m)
    orderBook = api.request(r)
    df = pd.DataFrame(r.response["orderBook"]["buckets"])

    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    # <現在レートの取得用URLの変数の設定>
    # /v3/accounts/{Account ID}/pricing 
    url = API_URL + "/v3/accounts/%s/pricing?instruments=%s" % (str(accountID), INSTRUMENT)
    # ヘッダー情報の変数の設定
    headers = {
                    "Authorization" : "Bearer " + access_token
                }
    # サーバーへの要求
    response = requests.get(url, headers=headers)
    # 処理結果の編集
    Response_Body = json.loads(response.text)
    currentPrice = float(Response_Body["prices"][0]["bids"][0]["price"])
    targetPriceList = []
    shortOrderList = []
    longOrderList = []
    checked=""
    shortTargetPrice =[]
    longTargetPrice = []

    for i in range(len(df)):
        checked=orderBook['orderBook']['buckets'][i]['price']
        if(float(checked) >currentPrice -1):
            if (float(checked) <currentPrice+1):
                longCountPercentOrder = float(orderBook['orderBook']['buckets'][i]['longCountPercent'])
                shortCountPercentOrder = float(orderBook['orderBook']['buckets'][i]['shortCountPercent'])
                if (longCountPercentOrder >1):
                    longOrderList.append(orderBook['orderBook']['buckets'][i])
                    longTargetPrice.append(orderBook['orderBook']['buckets'][i]['price'])
                if (shortCountPercentOrder >1):
                    shortOrderList.append(orderBook['orderBook']['buckets'][i])
                    shortTargetPrice.append(orderBook['orderBook']['buckets'][i]['price'])

    buy_Stop = 0 #逆指値の買い（順ばり）
    buy_Limit = 0 #指値の買い（逆ばり）
    sell_Stop = 0 #逆指値の売り（順ばり）
    sell_Limit = 0 #指値の売り（逆ばり）
    for i in range(len(longTargetPrice)):
        if(float(longTargetPrice[i]) > currentPrice):
            buy_Stop = float(longTargetPrice[i]) 
            try:
                while(float(longTargetPrice[i]) >currentPrice):
                    i -=1
                buy_Limit = float(longTargetPrice[i]) 
            except:
                pass
            break
    if(buy_Stop == 0):
        try:
            longTargetPrice.sort(reverse=True)
            buy_Limit = float(longTargetPrice[0])
        except:
            pass

    for i in range(len(shortTargetPrice)):
        if(float(shortTargetPrice[i]) > currentPrice):
            sell_Limit = float(shortTargetPrice[i]) 
            try:
                while(float(shortTargetPrice[i]) > currentPrice):
                    i -= 1
                sell_Stop = float(shortTargetPrice[i]) 
            except:
                pass
            break
    if(sell_Stop == 0):
        try:
            shortTargetPrice.sort(reverse=True)
            sell_Limit = float(shortTargetPrice[0])
        except:
            pass
    targetPriceList.append(buy_Stop)
    targetPriceList.append(buy_Limit)
    targetPriceList.append(sell_Stop)
    targetPriceList.append(sell_Limit)
    print("The current price is "+ str(currentPrice) +". The short/long count percent is " + str(targetPriceList) +" (逆指値買い、指値買い、逆指値売り、指値売り)")
    return targetPriceList

def orderFlexible(target, buysell, stoplimit,percent):
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    r = accounts.AccountSummary(accountID)
    acc = api.request(r)
    orderUnits = acc['account']['balance']

    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
        
    # 注文用URLの変数の設定 その１
    url = API_URL + "/v3/accounts/%s/orders" % str(accountID)
    
    # ヘッダー情報の変数の設定
    headers = {
                "Content-Type" : "application/json", 
                "Authorization" : "Bearer " + access_token
            }  
    # #データ情報の変数の設定
    try:
        orderUnits = float(orderUnits)
        orderUnits =math.floor(orderUnits)
    except:
        orderUnits = 1

    price = float(target)
    if(price !=0):
        Pip_location = -2
        TP_pips = 10 #pips
        SL_pips = 10 #pips
        if(buysell=="BUY"):
            orderUnits = orderUnits*percent
            TP_distance = round(price + TP_pips * (10**Pip_location),3)
            SL_distance = round(price - SL_pips * (10**Pip_location),3)
        else:
            orderUnits = -1*orderUnits*percent
            TP_distance = round(price - TP_pips * (10**Pip_location),3)
            SL_distance = round(price + SL_pips * (10**Pip_location),3)

        startTime = datetime.datetime.utcnow()
        startTime = int(startTime.strftime("%H"))
        finish = 4- (startTime%4)
        cancelTime = datetime.datetime.utcnow()+ datetime.timedelta(hours = finish)
        cancelTime = timeModified(cancelTime)
        print("canceltime should be " +str(cancelTime))
        if(stoplimit =="STOP"):
            typeOfOrder = "STOP"
        else:
            typeOfOrder = "LIMIT"

        data_Market = {
                        "order": {
                                "units": str(orderUnits),
                                "price": str(price),
                                "instrument": "USD_JPY",
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                "type": typeOfOrder,
                                "positionFill": "DEFAULT",
                                #TP
                                "takeProfitOnFill" : {
                                    "price": str(TP_distance),
                                    "timeInForce": "GTD",
                                    "gtdTime":str(cancelTime),
                                    }, 
                                #SL
                                "stopLossOnFill" : {
                                    "price": str(SL_distance),
                                    "timeInForce": "GTD",
                                    "gtdTime":str(cancelTime),
                                    }   
                                }
                        }
        
        data = json.dumps(data_Market)
        orderId =''
        try:
            # サーバーへの要求
            Response_Body = requests.post(url, headers=headers, data=data)
            # エラー発生時に例外処理へ飛ばす
            Response_Body.raise_for_status()

            #結果の表示
            print("注文が確定しました")
            print(json.dumps(Response_Body.json(), indent=2))

            print("オーダーIDは以下です")
            orderIdList=[]
            orderId = json.dumps(Response_Body.json()['orderCreateTransaction']['id'])
            print(orderId)
        #例外処理
        except Exception as e:
                if "Response_Body" in locals(): # or vars()
                        print("Status Error from Server(raise) : %s" %Response_Body.text)
                
                print("エラーが発生しました。\nError(e) : %s" %e)

        return orderId
# ------------------------------------
def letsGetStarted():
    jobfirst = Thread(target=job1)
    jobsecond = Thread(target=job2)
    jobthird = Thread(target=job3)
    jobfirst.start()
    jobsecond.start()
    jobthird.start()

sched = BlockingScheduler()

# Schedules job_function to be run from mon to fri
# sched.add_job(letsGetStarted, 'cron',  day_of_week='mon-fri', hour=0, minute=5)
# sched.start()
# letsGetStarted()

job2()




