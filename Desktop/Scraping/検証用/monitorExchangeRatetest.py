import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from time import sleep
import time
import math
import datetime
from WriteDBAndReporttest import readDatafromdataDB, createAndWriteDB, getOneYearAgo, makeCSVfiles
# from .WriteDBAndReporttest import readDatafromdataDB, createAndWriteDB

# class monitorExchangeRate:



def getCandles(date, time):
    oneHourAgo = date - datetime.timedelta(hours=time) 
    now = oneHourAgo + datetime.timedelta(hours=1) 
    winterOrSummer = int(now.strftime("%m%d"))
    date = now.strftime('%A')
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
    count = 720
    url = API_URL + "/v3/instruments/%s/candles?count=%s&price=M&granularity=S5&smooth=True&from=%s" % (INSTRUMENT, count,date_from)
    # ヘッダー情報の変数の設定
    headers = {
                    "Authorization" : "Bearer " + API_access_token
        }
    # サーバーへの要求
    try:
        response = requests.get(url, headers=headers)
        Response_Body = response.json()
    except:
        Response_Body = ""
    # 処理結果の編集
    
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
    try:
        # print("直前1分間のPCC")
        pcc1min = getEachPCC(ClassList, maximum, 12)
        # print("直前5分間のPCC")
        pcc5min = getEachPCC(ClassList, maximum, 60)
        # print("直前10分間のPCC")
        pcc10min =getEachPCC(ClassList, maximum, 120)
        # print("直前30分間のPCC")
        pcc30min = getEachPCC(ClassList, maximum, 360)
        # print("直前60分間のPCC")
        pcc60min = getEachPCC(ClassList, maximum,maximum)
        pcctotal = pcc1min*0.03 + pcc5min*0.07 + pcc10min*0.15 +pcc30min*0.25 + pcc60min*0.5
        pcctotal = str(pcctotal)
        print("I can conclude that the pcc during the period is " + pcctotal)
        return float(pcctotal)
    except:
        text = "You have an error for getting a pcc. This is probably due to the number of pcc we got which is most likely 0..."
        # main(text, "errorcode=404: PCC not found")
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
    ChoppedStr3 = ChoppedStr2[0].split(":")
    ChopppedStr4 = ChoppedStr3[0]+":00:00"
    modifiedTime = choppedStr[0] +"T"+ChopppedStr4 + ".000000000Z"
    return modifiedTime


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
        # print("The pearson correlation coeffcient is " + str(r))
    except:
        r = 0
        print(r)
    return r

def job1(repeat):
    now = datetime.datetime.utcnow()
    time = 24
    for n in range(repeat):
        now = now + datetime.timedelta(hours=24)
        date = getOneYearAgo(now)
        for i in range(24):
            pcc = getCandles(date, time)
            createAndWriteDB(date, time, pcc)
            readDatafromdataDB()
            time -=1
        time = 24
    makeCSVfiles()
    
    
# job1()
