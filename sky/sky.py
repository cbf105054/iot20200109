from machine import Pin,PWM
import time, network,urequests,ujson
import ESP8266WebServer
import dht

#取得溫濕度
sensor = dht.DHT11(Pin(0))
sensor.measure()
temp_humi = "溫度:{}℃，濕度:{}%".format(sensor.temperature(),sensor.humidity())
#time.sleep(3)

#控制RGB
rLED=PWM(Pin(4))
gLED=PWM(Pin(0))
bLED=PWM(Pin(2))

def setDuty(r,g,b):
    rLED.duty(r)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
    gLED.duty(g)
    bLED.duty(b)

def ledlight(aqi):
    if aqi<=50:
        setDuty(0,1023,0)
    elif 51 < aqi and  aqi<=100:
        setDuty(1023,300,0)
    else:
        setDuty(1023 ,0,0)
   
#連接網路
sta_if=network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('TL-3F','0911275826')
while not sta_if.isconnected():
    pass
print("Wifi以連上")
c=0
place=[]
AQI=[]
# def function(c):
#取得AQI空汙指數
res=urequests.get("http://opendata.epa.gov.tw/webapi/Data/REWIQA/?$filter=County%20eq%20%27%E5%B1%8F%E6%9D%B1%E7%B8%A3%27&$orderby=SiteName&$skip=0&$top=1000&format=json")

while c<4:
    j=ujson.loads(res.text)
    place.append("測站名稱:"+j[c]["SiteName"]+"<br>"+"發布時間:"+j[c]["PublishTime"]+"<br>"+"空汙狀態:"+j[c]["Status"]+"<br>"+"AQI:"+j[c]["AQI"]+"<br>"+"PM2.5:"+j[c]["PM2.5"]+"<br>")   
    AQI.append(int(j[c]["AQI"]))
    c+=1

        
show="<!DOCTYPE html>"+"<html><head><meta charset='UTF-8'></head><title>屏東觀測站</title><body>現在溫溼度為：<br><br><input id=\"Pingtung\" type=\"button\" value=\"屏東\" onclick=\"javascript:location.href ='/aaa?city=Pingtung'\"/>"+"<input id=\"Ryukyu\" type=\"button\" value=\"琉球\" onclick=\"javascript: location.href='/aaa?city=Ryukyu'\"/>"+"<input id=\"Hengchun\" type=\"button\" value=\"恆春\" onclick=\"javascript: location.href =\'/aaa?city=Hengchun\'\"/><br>"

def handledCmd(socket, args):
    if 'city' in args:
        if args['city'] == 'Pingtung':
            showpage=show+place[0]+"<br></body></html>"
            ledlight(AQI[0])
            ESP8266WebServer.ok(socket,"200",showpage)
        elif args['city'] == 'Ryukyu':
            showpage=show+place[1]+"<br></body></html>"
            ledlight(AQI[1])
            ESP8266WebServer.ok(socket,"200",showpage)
        elif args['city'] == 'Hengchun':
            showpage=show+place[2]+"<br></body></html>"
            ledlight(AQI[2])
            ESP8266WebServer.ok(socket,"200",showpage)
    else:
        showpage=show+"</body></html>"
        ESP8266WebServer.ok(socket,"200",showpage)
              
ESP8266WebServer.begin(80)
ESP8266WebServer.onPath("/aaa",handledCmd)
print ("伺服器位址:"+sta_if.ifconfig()[0])
while True:
    ESP8266WebServer.handleClient()