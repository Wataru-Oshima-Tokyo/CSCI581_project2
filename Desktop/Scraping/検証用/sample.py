import random
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from time import sleep
import time
import math
import datetime
import json


temp = 0
totalweekDays = 244
attempt = totalweekDays*24
initialValue = 100000
finalValue = initialValue
for i in range(attempt):
    a = random.randint(2,14)
    if(a%2==0):
        finalValue = finalValue*1.025 
        finalValue -=100
        temp +=1
    else:
        finalValue = finalValue*0.975 
        finalValue -=100
    if(finalValue <0):
        break

percent = (temp/attempt)*100
print(percent)
print("If you do fx with the rate of win :" +str(percent)+"%, then your initial value will be from " + str(initialValue)+" yen to " + str(finalValue) +"yen")


