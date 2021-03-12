import csv
import pandas as pd
import datetime
import sendEmailtoTheUsertest
import sqlite3
import psycopg2
import time

def makeCSVfiles():
    now = datetime.datetime.now()
    now = getOneYearAgo(now)
    todays_date = str(now.strftime("%Y%m%d")) 
    dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    # dbをpandasで読み出す。
    dfdata = pd.read_sql('SELECT * FROM data', conn)
    # dfresult = pd.read_sql('SELECT * FROM percent', conn)
    try:
        # result = todays_date+"result"
        data = todays_date+"data" 
        dfdata.to_csv('/Users/wataruoshima/Desktop/Scraping/検証用/' + "data" + ".csv", encoding='utf_8_sig')
        # dfresult.to_csv('/Users/wataruoshima/Desktop/Scraping/検証用/' + result + ".csv", encoding='utf_8_sig')
        print("success to convert to csv file")
    except:
        print("failed to convert to csv file")
    cur.close()
    conn.close()


def getOneYearAgo(now):
    date = str(now)
    choppedStr = date.split(" ")
    year = choppedStr[0].split("-")
    oneYearAgoInt = int(year[0])-3
    oneYearAgo = str(oneYearAgoInt) + "-"+year[1] + "-"+year[2] 
    ChoppedStr2 = choppedStr[1].split(".")
    modifiedTime = str(oneYearAgo) +" "+ChoppedStr2[0]
    date_time_obj = datetime.datetime.strptime(modifiedTime, '%Y-%m-%d %H:%M:%S')
    return date_time_obj

def reportThePCC(content):
    title = "PCCtest"
    sendEmailtoTheUser.main(content, title)

def readDatafromdataDB():
    now =datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
    conn = sqlite3.connect(dbname)
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
    # reportThePCC(content)
    cur.close()
    conn.close()

def readDatafromresultDB():
    dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
    conn = sqlite3.connect(dbname)
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
    dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
    conn = sqlite3.connect(dbname)
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
    dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
    conn = sqlite3.connect(dbname)
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

def createAndWriteDB(date, time, pcc):
    #日付を取得
    pcc =str(pcc)
    now = date - datetime.timedelta(hours=time)
    todays_date = str(now.strftime("%Y%m%d"))
    targetTime =  int(now.strftime("%H"))+9
    # 日付data.dbを作成する
    # すでに存在していれば、それにアスセスする。
    if (targetTime>=24):
        todays_date = int(todays_date) +1
        todays_date = str(todays_date)
        targetTime -=24
    if(targetTime <10):
        current_time = 'h0' + str(targetTime)
    else:
        current_time = 'h' + str(targetTime)
    dbname = '/Users/wataruoshima/Desktop/Scraping/検証用/testdata.db'
    conn = sqlite3.connect(dbname)
    # sqliteを操作するカーソルオブジェクトを作成
    cur = conn.cursor()
    # personsというtableを作成してみる
    # 大文字部はSQL文。小文字でも問題ない。
    try:
        cur.execute('CREATE TABLE data(id INTEGER PRIMARY KEY, date text, time text, PCC60min text)')
    except:
        pass
    #日付を入れる
    # "PCC"に"pcc(引数）"を入れる
    try:
        # cur.execute('ALTER TABLE data')
        cur.execute("INSERT INTO data(date, time, PCC60min) VALUES(?,?,?);" ,(todays_date, current_time, pcc))
        print("success to insert info into data")
        conn.commit()
    except:
        print("failed to insert info into data")
    #いらない欄を消す
    # sql = 'DELETE FROM data WHERE id=?'
    # データベースへコミット。これで変更が反映される。  
    
    cur.execute('SELECT * FROM data')
    # print(cur.fetchall())
    cur.close()
    # データベースへのコネクションを閉じる。(必須)
    conn.close()

