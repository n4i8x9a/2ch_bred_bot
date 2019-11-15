# Created by Alex Nix (@n4i8x9a) ©2019

# Version for VK.COM . More info in vk.com/dev .

# You need to install vk_api, beautifulsoup4 from pip .
import requests
import vk_api
import json
from http.client import HTTPSConnection
from json import dumps, loads
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from bs4 import BeautifulSoup
from vk_api import VkUpload

""""
def random_org(min,max)

This function gives you true random integer number from selected interval.
You need to register account on random.org and create API token.
"""
def random_org(min, max):      #minimum(min) and maximum(max) numbers of interval
    API_TOKEN = 'YOUR_RANDOM.ORG_TOKEN_IS_HERE'

    """
    more about request to random.org
    https://api.random.org/json-rpc/1/introduction
    """
    request_data = {
        'jsonrpc': '2.0',
        'method': 'generateIntegers',
        'params': {
            'apiKey': API_TOKEN,
            'min': min,  # Minimum number of interval.
            'max': max,  # Maximum number of interval.
            'n': 1,  # Number of requested numbers. In our case n=1.
        },
        'id': 1,
    }

    encoded_data = dumps(request_data)

    headers = {
        'Content-Type': 'application/json-rpc',  # type of request
    }
    encoded_headers = dumps(headers)

    connection = HTTPSConnection('api.random.org')
    connection.request('GET', '/json-rpc/1/invoke', encoded_data, headers)

    response = connection.getresponse()
    response_data = loads(response.read().decode())

    return response_data['result']['random']['data'][0]    # Return true random integer number.


# More info in vk.com/dev .

vk_session = vk_api.VkApi(token="YOUR_VK.COM_COMMUNITY_TOKEN_IS_HERE")
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, "YOUR_VK.COM_COMMUNITY_ID_IS_HERE")
session = requests.Session()
upload = VkUpload(vk_session)

while True :
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:  # If bot get a new message.
                if event.obj.text != '':  # If message is not empty.
                    if event.from_user:
                        if event.obj.text.lower()[0] == "/" and event.obj.text .find(' ')==-1 and len(event.obj.text)>1 and event.obj.text.lower()[-1]!="/":
                            # Bot gets the name of the board in the format "/NAME_OF_BOARD". For example : "/a", "/b", "/pr", etc.

                            # More info in 2ch.hk/api .
                            ro = requests.get("https://2ch.hk" + event.obj.text.lower() + "/catalog.json")  # Request to 2ch.hk .
                            if ro.status_code == 200:    # If board is exist .
                                zo = ro.json()   # JSON object with data from 2ch.hk .
                                _threads = zo["threads"]  # List of threads.

                                iddd = random_org(0, len(_threads) - 1)   # Random index of list of threads.
                                ttr = _threads[iddd]      # Random thread.
                                imag = ttr["files"]      # List of media files in thread.
                                url = "2ch.hk" + event.obj.text.lower() + "/res/" + ttr['num'] + '.html'  #  URL of thread.
                                date = ttr['date']      # Date of publication of thread .

                                i_url = []   # List of links of media files in correct format.
                                for i in imag:   # Converting links of the media files to correct format.
                                    i_url.append("http://2ch.hk" + i['path'])

                                """
                                Posts on 2ch.hk stored in HTML format.
                                We convert them to simple text using the Beautiful Soup library and replacing individual HTML characters,
                                since the library does not always work correctly. Not all characters are listed here, so if necessary,
                                you can add the rest of the HTML characters to replace them.
                                """
                                tt = ttr['comment'].replace("<br>", "\n")   # Text of thread with converted ends of lines.
                                tt = tt.replace("&#47;", "/")  # Convert to correct format "/" .
                                tt = tt.replace("&quot;", "\"")  # Convert to correct format quots  .
                                # You can replace other characters in the same way.

                                soup = BeautifulSoup(tt, features="html.parser")  # Using the Beautiful Soup library to convert text .

                                orr = ''  # If Original Post .
                                if ttr['op']:
                                    orr = "OP" + '\n.\n'

                                # Creating the text of VK Message .
                                mess = orr + date + '\n.\n' + '№ ' + ttr['num'] + '\n.\n' + ttr['name'] + '\n.\n' + ttr[
                                    'subject'] + '\n.\n.\n' + soup.get_text() + '\n.\n' + url
                                mess = mess.replace("&#47;", "/")
                                mess = mess.replace("&quot;", "\"")

                                if len(mess) >= 4096:   # If message longer than 4096 characters .
                                    vk.messages.send(user_id=event.obj.from_id, message=mess[:4096] , random_id=get_random_id())
                                    vk.messages.send(user_id=event.obj.from_id, message=mess[4096:], random_id=get_random_id())
                                else:
                                    vk.messages.send(user_id=event.obj.from_id, message=mess, random_id=get_random_id())


                                # Here bot trying to send pictures from thread. More info in vk.com/dev .
                                broken_links = ''    # Pictures that could not be attached as well as other type of media files.

                                attachments=[]     # List of attachments in VK MESSAGE .
                                for i in i_url:
                                    print(i)
                                    if i[-3:] == 'jpg' or i[-3:] == 'png': # If file is image .
                                        if len(attachments)>=10: # We can attach up to 10 attachments to one message.
                                            vk.messages.send(user_id=event.obj.from_id,
                                                             random_id=get_random_id(),
                                                             attachment=','.join(attachments))
                                            attachments=[]
                                        try:
                                            image = session.get(i, stream=True)
                                            photo = upload.photo_messages(photos=image.raw)[0]

                                            attachments.append(
                                                'photo{}_{}'.format(photo['owner_id'], photo['id'])
                                            )
                                        except Exception as exep:
                                            print(exep)
                                            print("error photo")
                                            broken_links += i + '\n'  # Adding link of image that failed to send.
                                    else:
                                            broken_links += i + '\n'  # Adding link of file that is not image .
                                if  len(attachments)>0:
                                    try:
                                        vk.messages.send(user_id=event.obj.from_id,
                                                         random_id=get_random_id(),
                                                         attachment=','.join(attachments))
                                    except Exception as exep:
                                        print (exep)
                                        for i in attachments:
                                            broken_links+=i+'\n'  # Adding link of image that failed to send.

                                if broken_links != '':   #  Sending the links of not image files and images that failed to send.
                                    vk.messages.send(user_id=event.obj.from_id, message=broken_links, random_id=get_random_id())
                                _threads = []

                            else:   # If user selected the board that not exist .
                                vk.messages.send(user_id=event.obj.from_id, message="Раздел неверно указан или не существует.",random_id=get_random_id())


                        else:   # If user send a wrong command.
                            vk.messages.send(user_id=event.obj.from_id, message="Не понел. Пиши название раздела, например /a , /b  . ",random_id=get_random_id())

                    """
                    Also, the bot can work in group chat. You can uncomment this text for example :
                    if event.from_chat:
                        if event.obj.text.lower()[0] == "/" and event.obj.text .find(' ')==-1 and len(event.obj.text)>1 and event.obj.text.lower()[-1]!="/":
                            ro = requests.get("https://2ch.hk" + event.obj.text.lower() + "/catalog.json")  
                            if ro.status_code == 200:    
                                zo = ro.json()  
                                _threads = zo["threads"]  

                                iddd = random_org(0, len(_threads) - 1)   
                                ttr = _threads[iddd]     
                                imag = ttr["files"]      
                                url = "2ch.hk" + event.obj.text.lower() + "/res/" + ttr['num'] + '.html'  
                                date = ttr['date']     

                                i_url = []   
                                for i in imag:   
                                    i_url.append("http://2ch.hk" + i['path'])

                               
                                tt = ttr['comment'].replace("<br>", "\n")   
                                tt = tt.replace("&#47;", "/")  
                                tt = tt.replace("&quot;", "\"")  
                                

                                soup = BeautifulSoup(tt, features="html.parser")  

                                orr = ''  
                                if ttr['op']:
                                    orr = "OP" + '\n.\n'

                                
                                mess = orr + date + '\n.\n' + '№ ' + ttr['num'] + '\n.\n' + ttr['name'] + '\n.\n' + ttr[
                                    'subject'] + '\n.\n.\n' + soup.get_text() + '\n.\n' + url
                                mess = mess.replace("&#47;", "/")
                                mess = mess.replace("&quot;", "\"")

                                if len(mess) >= 4096:   
                                    vk.messages.send(chat_id=event.chat_id, message=mess[:4096] , random_id=get_random_id())
                                    vk.messages.send(chat_id=event.chat_id, message=mess[4096:], random_id=get_random_id())
                                else:
                                    vk.messages.send(chat_id=event.chat_id, message=mess, random_id=get_random_id())


                               
                                broken_links = ''    

                                attachments=[]     
                                for i in i_url:
                                    print(i)
                                    if i[-3:] == 'jpg' or i[-3:] == 'png':
                                        if len(attachments)>=10: 
                                            vk.messages.send(chat_id=event.chat_id,
                                                             random_id=get_random_id(),
                                                             attachment=','.join(attachments))
                                            attachments=[]
                                        try:
                                            image = session.get(i, stream=True)
                                            photo = upload.photo_messages(photos=image.raw)[0]

                                            attachments.append(
                                                'photo{}_{}'.format(photo['owner_id'], photo['id'])
                                            )
                                        except Exception as exep:
                                            print(exep)
                                            print("error photo")
                                            broken_links += i + '\n'  
                                    else:
                                            broken_links += i + '\n'  
                                if  len(attachments)>0:
                                    try:
                                        vk.messages.send(chat_id=event.chat_id,
                                                         random_id=get_random_id(),
                                                         attachment=','.join(attachments))
                                    except Exception as exep:
                                        print (exep)
                                        for i in attachments:
                                            broken_links+=i+'\n'  

                                if broken_links != '':   
                                    vk.messages.send(chat_id=event.chat_id, message=broken_links, random_id=get_random_id())
                                _threads = []

                            else:   
                                vk.messages.send(chat_id=event.chat_id, message="Раздел неверно указан или не существует.",random_id=get_random_id())


                        else:   
                            vk.messages.send(chat_id=event.chat_id, message="Не понел. Пиши название раздела, например /a , /b  . ",random_id=get_random_id())
 
                    """


    except Exception as exep:
        print(exep)
        continue

        

# Created by Alex Nix (@n4i8x9a) ©2019