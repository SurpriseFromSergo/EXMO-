
№Разработал SurpriseFromSergo (SergoDeveloper)
#Импорт библиотек ExmoAPI
import sys
import http.client
import urllib
import json
import hashlib
import hmac
import time
import requests
#для отправки сообщений по емейлу
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

        
class ExmoAPI:
    def __init__(self, API_KEY, API_SECRET, API_URL = 'api.exmo.com', API_VERSION = 'v1'):
        self.API_URL = API_URL
        self.API_VERSION = API_VERSION
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')

    def sha512(self, data):
        H = hmac.new(key = self.API_SECRET, digestmod = hashlib.sha512)
        H.update(data.encode('utf-8'))
        return H.hexdigest()

    def api_query(self, api_method, params = {}):
        params['nonce'] = int(round(time.time() * 1000))
        params =  urllib.parse.urlencode(params)

        sign = self.sha512(params)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Key": self.API_KEY,
            "Sign": sign
        }
        conn = http.client.HTTPSConnection(self.API_URL)
        conn.request("POST", "/" + self.API_VERSION + "/" + api_method, params, headers)
        response = conn.getresponse().read()

        conn.close()

        try:
            obj = json.loads(response.decode('utf-8'))
            if 'error' in obj and obj['error']:
                print(obj['error'])
                raise sys.exit()
            return obj
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response)
            raise sys.exit()
    

#переменные и константы
# Параметры пользователя
BTC_K = 'your key'
BTC_S = 'your secret'
pairs = ['XRP_RUB','BTC_RUB','USD_RUB','SMART_RUB','USDT_RUB','KICK_RUB'] # список валютных пар, которые вас интересуют(указываются. как заданы в результате запроса https://api.exmo.com/v1/ticker/)
codes = [1]
# 1 - цена посл. сделки выше средней
# 2 - цена посл. сделки ниже средней
# 3 - цена посл. сделки ниже Минимума дня
# 4 - цена посл. сделки выше Максимума дня
#время через которое каждый раз анализируется рынок в минутах
timer=30
#кол-во проверок (цикл не должен вечно работать)
countChecks=6


#метод отправки сообщений для яндекс аккаунта
def send_mail(zag, text):
    login = 'ваш логин @yandex.ru'
    password='Пароль от почты'
    url = 'smtp.yandex.ru'
    toaddr = 'Куда хотите отправить, можете самому себе@yandex.ru'
    
    msg = MIMEMultipart()
    msg['Subject'] = zag
    msg['From'] =  'От кого: адресс вашей почты'
    body = text
    msg.attach(MIMEText(body,'plain'))
    
    try:
        server=smtplib.SMTP_SSL(url, 465)
    except TimeoutError:
        print ('no connect')
    server.login(login,password)
    server.sendmail(login,toaddr,msg.as_string())
    server.quit()
    
def main():
    #основной код
    # Установим начальные данные для соединения
    eAPI = ExmoAPI(BTC_K, BTC_S)
    
    #главный циккл
    launch=True
    while(launch):
        ticker=eAPI.api_query("ticker/")
        otchet=''
        add=0
        for pair in pairs:
            last_trade=ticker[pair]['last_trade']
            sell_price=ticker[pair]['sell_price']
            buy_price=ticker[pair]['buy_price']
            high=ticker[pair]['high']
            low=ticker[pair]['low']
            avg=ticker[pair]['avg']
            if codes.count(1) is not 0:
                if(last_trade>avg):
                    otchet=otchet+'\n Валютная пара '+pair+'\nЦена последней сделки выше средней.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price
                    print('Валютная пара'+pair+'\nЦена последней сделки выше средней.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price)
                    add=add+1
            if codes.count(2) is not 0:
                if(last_trade<avg):
                    otchet=otchet+'\n Валютная пара '+pair+'\nЦена последней сделки ниже средней.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price
                    print('Валютная пара'+pair+'\nЦена последней сделки ниже средней.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price)
                    add=add+1
            if codes.count(3) is not 0:
                if(last_trade<low):
                    otchet=otchet+'\n Валютная пара '+pair+'\nЦена последней сделки ниже минимума дня.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price
                    print('Валютная пара'+pair+'\nЦена последней сделки ниже минимума дня.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price)
                    add=add+1
            if codes.count(4) is not 0:
                if(last_trade>high):
                    otchet=otchet+'\n Валютная пара '+pair+'\nЦена последней сделки выше максимума дня.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price
                    print('Валютная пара'+pair+'\nЦена последней сделки выше максимума дня.'+'\n Макс.='+high+'\n Средняя цена='+avg+'\n Мин.='+low+'\n sell стакана='+sell_price+'\n buy стакана='+buy_price)
                    add=add+1
        if add is not 0:
            send_mail('EXMO',otchet)
            add=0
        time.sleep(timer*60)
        
        #выключатель
        countChecks = countChecks -1
        print(countChecks)
        if(countChecks is 0):
            break
    print('программа остановилась\n Все. я отработал, хочу спать')
            

if __name__=="__main__":
    main()
    



