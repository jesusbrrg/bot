import requests
import datetime
import demiurge, sys, getopt, os, pickle, tempfile
import pymongo


#open mongoclient from mlab

from pymongo import MongoClient
mongo_uri = "mongodb://wallabot:wallabot@ds129906.mlab.com:29906/wallabot?authMechanism=SCRAM-SHA-1"
client = MongoClient(mongo_uri)
db = client.wallabot
data_collection = db.data
properties_collection = db.properties


#Get properties
properties = properties_collection.find_one({"type":"prod_properties"})
properties_data = properties.get('data')
properties_data_telegram = properties_data.get('telegram')
properties_data_wallapop = properties_data.get('wallapop')

telegram_enable = properties_data_telegram.get('enable')
telegram_token = properties_data_telegram.get('token')
telegram_chat_id = properties_data_telegram.get('chat_id')
wallapop_keys = properties_data_wallapop.get('keys')
wallapop_lat = properties_data_wallapop.get('lat')
wallapop_lng = properties_data_wallapop.get('lng')
wallapop_maxPrice = properties_data_wallapop.get('maxPrice')

#Write mongo
def writeData(visit_elem):
    data_collection.insert_one({"uri":visit_elem})

#find mongo
def existData(visit_elem):
    elem = data_collection.find_one({"uri":visit_elem})
    if(elem):
        return True
    else:
        return False


#WALLAPOP CONFIG
urlWallapop = 'https://es.wallapop.com'
urlWallapopMobile = 'http://p.wallapop.com/i/'

#Telegram bot handler
class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)
        

    def get_updates(self, offset=None, timeout=1):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text,'parse_mode':'html','disable_web_page_preview':True}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def send_photo(self,chat_id,photo_url):
        params = {'chat_id':chat_id, 'photo':photo_url}
        method = 'sendPhoto'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()
        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = [] 
        return last_update


#Demiurge scrap for wallapop
class Products(demiurge.Item):
    title = demiurge.TextField(selector='span.product-info-title')
    price = demiurge.TextField(selector='span.product-info-price')
    url = demiurge.AttributeValueField(selector='div.card-product a:eq(0)', attr='href')
    image_url = demiurge.AttributeValueField(selector='img.card-product-image', attr='src')
    class Meta:
        selector = 'div.card-product'

class ProductDetails(demiurge.Item):
    description = demiurge.TextField(selector='p.card-product-detail-description')
    location = demiurge.TextField(selector='div.card-product-detail-location')
    class Meta:
        selector = 'div.card-product-detail'



#alert 
def wallAlert(urlSearch,key):
    # Load after data search
    data_temp = []

    
    # Read web
    results = Products.all(urlSearch)
    
    for item in results:
        data_temp.append({'title': item.title
                          , 'price': item.price
                          , 'url': item.url 
                          , 'image_url' : item.image_url})

   
   
    # Check new items
    list_news = []
    for item in data_temp:
        if not existData(item.get('url')):
            list_news.append(item)    

    
    if not list_news:
        telegram_handler.send_message(telegram_chat_id,"Nada nuevo de "+key)
    else:
        for item in list_news:
            # Get info from new items
            title = item['title'] + " - " + item['price']
            url = item['url']
            image_url = item['image_url']
            productID = url.split("-")[-1]
            applink = urlWallapopMobile + productID
           
            # Send Alert
            writeData(url)

            if telegram_enable:
                telegram_handler.send_photo(telegram_chat_id,image_url)
                telegram_handler.send_message(telegram_chat_id,'<b>'+title+'</b>'+applink)
               
               
 


#MAIN
telegram_handler = BotHandler(telegram_token)

def main():
    #iteramos las keys
    
    for key in wallapop_keys:    
        #Busqueda informacion
        
        urlSearch = 'http://es.wallapop.com/search?kws=' + key + '&maxPrice='+wallapop_maxPrice+'&dist=500&order=creationData-des&publishDate=24&lat='+ wallapop_lat+'&lng='+wallapop_lng
        wallAlert(urlSearch,key)

     
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

			
