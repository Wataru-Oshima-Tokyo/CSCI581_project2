import datetime
import lxml
from bs4 import BeautifulSoup
import requests
from time import sleep
import re
import pandas as pd
import math 
import sqlite3
#local package
from  WriteDBAndReporttest import writeResult, readDatafromresultDBandShowTheRateOfWin,getOneYearAgo
from monitorExchangeRatetest import timeModified

def executeBuyOrSell(pcc, date, time, th):
    starttime = date - datetime.timedelta(hours=time)
    # endtime = starttime+datetime.timedelta(minutes=25)
    endtime = starttime+datetime.timedelta(minutes=15)
    winterOrSummer = int(starttime.strftime("%m%d"))
    API_access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"
    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    jststart = timeModified(starttime + datetime.timedelta(hours=9))
    date_from = timeModified(starttime)
    date_to = timeModified(endtime)
    print("ターゲットタイム（JST）は"+ str(jststart) + "から25分後") 
    # <ろうそく足取得用URLの変数の設定>
    # /v3/instruments/{Account ID}/candles 
    # if(winterOrSummer >310 and winterOrSummer < 1103):
    #     target1 = 'h14'
    #     target2 = 'h20'
    #     target3 = 'h00'
    # else:
    #     target1 = 'h14'
    #     target2 = 'h21'
    #     target3 = 'h01'
    # if(th == target1 or th == target2 or th ==target3):
    #     pcc *=-1
    #     if(th == target3):
    #         count = 2880
    #     else:
    #         count = 720
    # else:
    #     count =300 #二十五分間
    count =300
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
    openPrice = float(Response_Body["candles"][0]["mid"]["o"])
    closePrice = float(Response_Body["candles"][count-1]["mid"]["c"])
    highPrices = []
    lowPrices = []
    while i<count:
        try:
            highPrice = float(Response_Body["candles"][i]["mid"]["h"])
            lowPrice = float(Response_Body["candles"][i]["mid"]["l"])
        except:
            break
        highPrices.append(highPrice)
        lowPrices.append(lowPrice)
        i = i+1
    #get the prices
    result =0
    if(pcc>0):
        for i in range(len(highPrices)):
            if(highPrices[i]>openPrice+0.115):
                result=1
                break
            elif(lowPrices[i]<openPrice-0.1):
                result=-1
                break
            else:
                pass
        if(result == 0 and openPrice+0.015<closePrice):
            result = 1
        elif(result !=1):
            result =-1
        else:
            pass
    else:
        for i in range(len(lowPrices)):
            if(lowPrices[i]<openPrice-0.115):
                result=1
                break
            elif(highPrices[i]>openPrice+0.1):
                result=-1
                break
            else:
               pass
        if(result == 0 and openPrice-0.015>closePrice):
            result = 1
        elif(result !=1):
            result =-1
        else:
            pass
    print(result)
    return result

def readDataForInverse(targethour):
    overallPcc = 0
    eachPcc = 0
    if (targethour == "h14"):
        now = datetime.datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
        conn = sqlite3.connect(dbname)
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
        dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
        conn = sqlite3.connect(dbname)
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
        dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
        conn = sqlite3.connect(dbname)
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

def readData(targetDate, targethour, time):
    tarT = targethour.strip("h")
    tarT = int(tarT)

    # print(tarT)
    # sleep(800)
    todays_date = targetDate - datetime.timedelta(hours=time) + datetime.timedelta(hours=9)
    whatDate = str(todays_date.strftime("%A"))
    winterOrSummer = int(todays_date.strftime("%m%d"))
    todays_date = str(todays_date.strftime("%Y%m%d"))
    print(todays_date + ":" +whatDate)
    if(winterOrSummer > 310 and winterOrSummer <1103):
        ft = 6
    else:
        ft = 7
    if((whatDate == 'Monday' and tarT < ft) or (whatDate == 'Saturday' and tarT > ft) or whatDate == 'Sunday'):
        return 0
    else:
        dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()
        # dbをpandasで読み出す。
        # df = pd.read_sql('SELECT * FROM data', conn)
        cur.execute('SELECT * FROM data')
        # print(cur.fetchall())
        pcc60min =0.0
        for row in cur:
            if(todays_date == row[1]):
                if (row[2] ==targethour):
                    try:
                        pcc60min = float(row[3])
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

def bidOrAsk(pcc, date, time, th):
    rateOfWin = 0
    pcc = float(pcc)
    # I guess that you can modify the percent here as you see the pcc
    if (pcc>0):
        pcc =1
        rateOfWin = executeBuyOrSell(pcc, date, time, th)
    elif (pcc<0):
        pcc=-1
        rateOfWin = executeBuyOrSell(pcc, date, time, th)
    else: 
        print("not buy anything")
    return rateOfWin

def getTargetHour(date,time):
    now = date - datetime.timedelta(hours=time)
    todays_date = str(now.strftime("%Y%m%d"))
    targetTime =  int(now.strftime("%H"))+9
    # 日付data.dbを作成する
    # すでに存在していれば、それにアスセスする。
    if (targetTime>=24):
        targetTime -=24
    if(targetTime <10):
        current_time = 'h0' + str(targetTime)
    else:
        current_time = 'h' + str(targetTime)
    return current_time

def job3(repeat):
    now = datetime.datetime.utcnow()
    date = getOneYearAgo(now)
    time = 24
    attempt = []
    win =[]
    for n in range(repeat):
        now = now + datetime.timedelta(hours=24)
        date = getOneYearAgo(now)
        print("----------- start of the day ----------------------")
        for i in range(24):
            th = getTargetHour(date, time)
            if(th !='h01' or th !='h02' or th !='h03' or th !='h04' or th !='h05'):
                print("we take the pcc at " +th + ". and decide if bid or ask")
                pcc = readData(date, th, time)
                percent = bidOrAsk(pcc, date, time, th)
                if(percent!=0):
                    attempt.append(percent)
                time -=1
                # for i in attempt:
                if(percent > 0):
                    win.append(1)
                # Get the percent
                try:
                    result =(len(win)/len(attempt))*100
                    print("Your rate of win is " +str(result)+"%")
                except:
                    pass
        time = 24
        print("----------- end of the day ----------------------")
        

    
    



# tempjob()
# pcc = readData(date, th)
# print(pcc)
# result = executeBuyOrSell(pcc, date)
# print(result)