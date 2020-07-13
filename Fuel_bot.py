import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

bot = telebot.TeleBot('TOKEN')

URL = 'https://finance.i.ua/fuel/'
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}

cost_dict = {}

def parse(url, fuel_type, params=None):
    html = requests.get(url, headers=HEADERS, params=params)
    soup = BeautifulSoup(html.text, 'html.parser')    
    fuels = soup.find_all('tr')

    for fuel in fuels:
        try:
            if fuel_type == 'dp':
                title = fuel.find('th', class_='td-title').get_text(strip=True)
                fuel_cost = fuel.find('td', class_='dp').get_text(strip=True)
            elif fuel_type == 'a92':
                title = fuel.find('th', class_='td-title').get_text(strip=True)
                fuel_cost = fuel.find('td', class_='a_92').get_text(strip=True)
            elif fuel_type == 'a95':
                title = fuel.find('th', class_='td-title').get_text(strip=True)
                fuel_cost = fuel.find('td', class_='a_95').get_text(strip=True)

            cost={title:fuel_cost}
            cost_dict.update(cost)
        except AttributeError:
            pass
        except UnboundLocalError:
            pass

def sort(cost_dict):
    cost_list = list(cost_dict.items())
    cost_list.sort(key=lambda i: i[1])
    return cost_list[::-1]

@bot.message_handler(commands=['start'])
def btn(message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    a92 = types.KeyboardButton('A92')
    a95 = types.KeyboardButton('A95')
    dp = types.KeyboardButton('Diesel')
    markup.add(a92, a95, dp)
    bot.send_message(message.chat.id, "Выберите вид топлива:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def fuel(message):
    
    if message.text == 'Diesel':
        message.text = 'dp'
    else:
        pass
    
    cost_dict.clear()
    parse(URL, message.text.lower())

    btn = types.InlineKeyboardMarkup()    
    for i in sort(cost_dict):
        btn_fuel= types.InlineKeyboardButton(text=f'{i[0]} - {i[1]} грн/л', url=f'https://www.google.com/maps/search/автозаправка+{i[0]}')
        btn.add(btn_fuel)
    bot.send_message(message.chat.id, reply_markup = btn, text=f'Актуальные цены на {message.text}')
    
if __name__== "__main__":
    bot.polling(none_stop=True, timeout=999999)
