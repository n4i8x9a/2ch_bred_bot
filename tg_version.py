# Created by Alex Nix (@n4i8x9a) ©2019

# Version for TELEGRAM MESSENGER . More info in core.telegram.org .

# You need to install pytelegrambotapi, beautifulsoup4 from pip .
import time
import telebot;
from http.client import HTTPSConnection
from json import dumps, loads
import requests
import json
from bs4 import BeautifulSoup

""""
def random_org(min,max)

This function gives you true random integer number from selected interval.
You need to register account on random.org and create API token.
"""
def random_org(min, max):      # minimum(min) and maximum(max) numbers of interval
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


# More info in core.telegram.org .
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN_IS_HERE');
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global random_org

    if message.text.lower()[0] == "/" and message.text.find(' ')==-1 and len(message.text)>1 and message.text.lower()[-1]!="/":
        # Bot gets the name of the board in the format "/NAME_OF_BOARD". For example : "/a", "/b", "/pr", etc.

        # More info in 2ch.hk/api .
        ro = requests.get("https://2ch.hk"+message.text.lower()+"/catalog.json")  # Request to 2ch.hk .
        if ro.status_code==200:   # If board is exist .
            zo = ro.json()        # JSON object with data from 2ch.hk .
            _threads = zo["threads"]   # List of threads.

            iddd = random_org(0, len(_threads) - 1)   # Random index of list of threads.

            ttr = _threads[iddd]    # Random thread.
            imag = ttr["files"]     # List of media files in thread.
            url = "2ch.hk"+message.text.lower()+"/res/" + ttr['num'] + '.html'    #  URL of thread.
            date = ttr['date']    # Date of publication of thread .

            i_url = []     # List of links of media files in correct format.
            for i in imag:  # Converting links of the media files to correct format.
                i_url.append("http://2ch.hk" + i['path'])

            """
            Posts on 2ch.hk stored in HTML format.
            We convert them to simple text using the Beautiful Soup library and replacing individual HTML characters,
            since the library does not always work correctly. Not all characters are listed here, so if necessary,
            you can add the rest of the HTML characters to replace them.
            """
            tt = ttr['comment'].replace("<br>", "\n")  # Text of thread with converted ends of lines.
            tt = tt.replace("&#47;", "/")    # Convert to correct format "/" .
            tt = tt.replace("&quot;", "\"")   # Convert to correct format quots  .
            # You can replace other characters in the same way.
            soup = BeautifulSoup(tt, features="html.parser")  # Using the Beautiful Soup library to convert text .

            orr = ''   # If Original Post .
            if ttr['op']:
                orr = "OP" + '\n.\n'

            # Creating the text of Telegram Message .
            mess = orr + date + '\n.\n' + '№ ' + ttr['num'] + '\n.\n' + ttr['name'] + '\n.\n' + ttr[
                'subject'] + '\n.\n.\n' + soup.get_text() + '\n.\n' + url
            mess = mess.replace("&#47;", "/")
            mess = mess.replace("&quot;", "\"")

            if len(mess) >= 4096:   # If message longer than 4096 characters .
                bot.send_message(message.chat.id, mess[:4096], disable_web_page_preview=True)
                bot.send_message(message.chat.id, mess[4096:], disable_web_page_preview=True)
            else:
                bot.send_message(message.chat.id, mess, disable_web_page_preview=True)

            # Here bot trying to send pictures and other media files from thread. More info in core.telegram.org .
            broken_links=''   # Links of files that failed to send.

            for i in i_url:

                if i[-3:] == 'jpg' or i[-3:] == 'png':  # If image .
                    try:
                        bot.send_photo(message.chat.id, i.replace('/\n$/', ""))
                    except Exception as exep:
                        print(exep)
                        print("error photo")
                        broken_links+=i+'\n'  # If sending the image failed.

                elif i[-3:] == 'mp3':   # If audio.
                    try:
                        bot.send_audio(chat_id=message.chat.id, audio=i.replace('/\n$/', ""))
                    except Exception as exep:
                        print(exep)
                        print("error audio")
                        broken_links += i + '\n'  # If sending the audio failed.

                elif i[-3:] == 'mp4':  # If video.
                    try:
                        bot.send_video(chat_id=message.chat.id, data=i.replace('/\n$/', ""))
                    except Exception as exep:
                        print(exep)
                        print("error video")
                        broken_links += i + '\n' # If sending the video failed.

                else:   # If file of other type.
                    try:
                        bot.send_document(chat_id=message.chat.id, data=i.replace('/\n$/', ""))
                    except Exception as exep:
                        print(exep)
                        print("error document")
                        broken_links += i + '\n'  # If sending the file failed.

            if broken_links!='':  # Bot send the links of files failed to send.
                bot.send_message(message.from_user.id, broken_links)
            _threads = []


        else :    # If user selected the board that not exist .
            bot.send_message(message.from_user.id, "Раздел не существует или неверно указан.")


    else :    # If user send a wrong command.
        bot.send_message(message.from_user.id, "Не понел.")


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as exep:
        print(exep)
        continue


# Created by Alex Nix (@n4i8x9a) ©2019