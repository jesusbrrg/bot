import requests
import datetime
import demiurge, sys, getopt, os, pickle, tempfile



#AREA DE CONFIGURACION Y PARAMETROS

token = '504312938:AAE6YlVxjCg5e3iTu_a0v2MrJLTNoMqA_Yk'
wallapop_keys = ['cuchillo']
telegram_chat_id = '177115022'
prod = True
url_image_test = 'https://www.google.es/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'

##AREA CONFIGURACION WALLAPOP
urlWallapop = 'http://es.wallapop.com'
urlWallapopMobile = 'http://p.wallapop.com/i/'
SAVE_LOCATION = os.path.join(tempfile.gettempdir(), 'alertWallapop10.pkl')
data_save_check = True


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
        params = {'chat_id': chat_id, 'text': text}
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
    url = demiurge.AttributeValueField(selector='img.card-product-image', attr='src')
    class Meta:
        selector = 'div.card-product'

class ProductDetails(demiurge.Item):
    description = demiurge.TextField(selector='p.card-product-detail-description')
    location = demiurge.TextField(selector='div.card-product-detail-location')
    class Meta:
        selector = 'div.card-product-detail'



#METODO ANALISIS
def wallAlert(urlSearch):
    # Load after data search
    data_temp = []
    '''
    try:
        dataFile = open(SAVE_LOCATION, 'rb')
        data_save = pickle.load(dataFile)
    except:
        data_save = open(SAVE_LOCATION, 'wb')
        pickle.dump(data_temp, data_save)
        pass
    '''
    # Read web
    results = Products.all(urlSearch)
    
    for item in results:
        data_temp.append({'title': item.title
                          , 'price': item.price
                          , 'relativeUrl': item.url })

   
  '''
    # Check new items
    list_news = []
    if data_save_check and data_save != data_temp:
        for item in data_temp:
            if item not in data_save:
                list_news.append(item)
'''

    # Check new items
    list_news = []
    for item in data_temp:
        list_news.append(item)

    
    for item in list_news:
        # Get info from new items
        title = item['title'] + " - " + item['price']
        url = item['relativeUrl']
        #itemDetails = ProductDetails.one(url)
        #body = itemDetails.description + "\n" + itemDetails.location
        body=''
        productID = url.split("-")[-1]
        applink = urlWallapopMobile + productID

        # Send Alert
       
        if prod:
            telegram_handler.send_photo(telegram_chat_id,url)
            telegram_handler.send_message(telegram_chat_id,title+" <a href='"+url+">Click aqui</a>")
        

 

    # Save data
   # data_save = open(SAVE_LOCATION, 'wb')
    #pickle.dump(data_temp, data_save)





#MAIN

telegram_handler = BotHandler(token)

def main():
    #iteramos las keys
    
    for key in wallapop_keys:
        text_key = "analizando elemento: "+key
        
       
        #Busqueda informacion
        
        urlSearch = 'http://es.wallapop.com/search?kws=' + key + '&maxPrice=&dist=0_&order=creationData-des&lat=41.398077&lng=2.170432'
        
        wallAlert(urlSearch)

     
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

			
