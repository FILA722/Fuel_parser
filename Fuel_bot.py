"""
- добавить выбор области
- сделать счетчик стартов и циклов с записью в файл и выдачей результата по команде
"""

import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

# Test_bot
bot = telebot.TeleBot('TOKEN')

URL = 'https://maanimo.com/fuels'
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}


def parse(url, params=None):
    '''
    titles - данные со страницы, содержащие названиями АЗС 
    fuel_costs - данные со страницы, содержащие цены на топливо

    Эта функция парсит данные с названиями АЗС и ценами на топливо. 
    '''

    html = requests.get(url, headers=HEADERS, params=params)
    soup = BeautifulSoup(html.text, 'html.parser')

    titles = soup.find_all('td', class_='operator')
    fuel_costs = soup.find_all('span', class_='value')

    return titles, fuel_costs

def azs_titles(titles):
    '''
    azs_names - список с названиями АЗС

    Эта функция достает газвания АЗС и добавляет их в список azs_names
    '''
    azs_names = []
    for j in titles:
        title = j.find('span', class_='name').get_text(strip=True)
        azs_names.append(title)
    return azs_names

def costs(fuel_costs):
    '''
    cost_list - общий список всех цен с сайта
    cost_list_local - список цен, которые находятся в одной строке на странице.
    cost_list_all - список из списков cost_list_local. 

    Эта функция достает цены на АЗС и формирует их в float значения 
    Также тут прописаны условия, по которым cost_list разбивается на отдельные 
    cost_list_local. 
    '''

    #формирует значения флоат
    cost_list = []             # общий список всех цен с сайта 
    cost = ''                  # сюда добавляються все цифры и точки для формирования цены.
    for string in fuel_costs:
        for num in str(string):
            if num.isdigit() or num==',':
                cost = cost + num
            else:
                if cost!='':
                    cost = cost.replace(',','.')
                    cost_list.append(float(cost))
                    cost = ''
        if cost!='':
            cost_list.append(float(cost))

    #групируем цены по отдельным спискам, которые соответствуют строкам на странице.
    cost_list_all = []  
    cost_list_local = []

    for i in range(0, len(cost_list)-1):
        if cost_list[i] >= cost_list[i+1] :
            cost_list_local.append(cost_list[i])

        elif cost_list[i]<15:
            cost_list_local.append(cost_list[i])
            cost_list_all.append(cost_list_local)
            cost_list_local = []
        
        elif cost_list[i]<cost_list[i+1] and cost_list[i+1]<cost_list[i+2]:
            cost_list_local.append(cost_list[i])

        elif cost_list[i]<cost_list[i+1] and cost_list[i+1]>cost_list[i+2] and cost_list[i+2]>15:
            cost_list_local.append(cost_list[i])
            cost_list_all.append(cost_list_local)
            cost_list_local = []
        else:
            cost_list_local.append(cost_list[i])
                
    cost_list_local.append(cost_list[-1])
    cost_list_all.append(cost_list_local)
    
    #этот алгоритм добавляет "-" и "--" на места отсутствующих значений 
    for i in cost_list_all:
        if i[-1] > 15:
            i.append('-')
            if len(i)<5:
                i.insert(0, '--')
        elif len(i)<5:
            i.insert(0, '--')

    return cost_list_all

def title_and_cost_group(azs_names, cost_list_all):
    '''
    price_all - словарь с ключами из azs_titles (названия АЗС) и значениями - списками 
    из словарей, где ключи из fuel_types(разновидности топлива), а значения из cost_list_all(цены на топливо)
    price_local 
    fuel_dict - словарь с ключом из fuel_types(разновидности топлива) и значением из cost_list_all(цена на топливо)
    fuel_list_local - список и словариков fuel_dict
    fuel_list_all - список из списков fuel_list_local
    price_local - словарик, в котором ключ - название АЗС, а значение список fuel_list_local (типы топлива, которые относятся к этой АЗС и цены на эти топлива)
    price_all - общий словарь из словариков price_local

    Эта ф-ция сопоставляет типы топлива с ценами, присвает этим данный название АЗС и собирает все в один большой словарь
    '''

    price_all = {}
    price_local = {}
    fuel_list_all = []
    fuel_dict = {}

    #присваеваем видам топлива цены
    fuel_types = ['A95+', 'A95', 'A92', 'Diesel', 'GAS']
    for i in cost_list_all:
        fuel_list_local = []
        for j in range(0, len(fuel_types)):
            fuel_dict = {fuel_types[j]: i[j]}
            fuel_list_local.append(fuel_dict)
        fuel_list_all.append(fuel_list_local)
        
    #сопоставляем названия АЗС с даными из прошлого шаа
    for i in range(0, len(azs_names)):
        price_local = {azs_names[i]:fuel_list_all[i]}
        price_all.update(price_local)
    
    return price_all

def sort(fuel_type, azs_names, price_all):
    '''
    fuel_type - запрашиваемый тип топлива
    answer_dict - ключи - названия АЗС, значения - цена выбранного типа топлива(fuel_type)
    answer_list - список из значений (навание АЗС:цена) словаря answer_dict

    Эта ф-ция достает цену запрашеваемого типа топлива и сопостовляет его с названием АЗС
    Соберает эти данные в словарь answer_dict, и формирует отсортированый по значениям список из данных словаря answer_dict
    '''

    answer_dict = {}
    
    for i in azs_names:
        if fuel_type == 'A95+':
            if price_all[i][0]['A95+'] == '--':
                pass
            else:
                answer = {i : price_all[i][0]['A95+']}
                answer_dict.update(answer)
        elif fuel_type == 'A95':
            answer = {i : price_all[i][1]['A95']}
            answer_dict.update(answer)
        elif fuel_type == 'A92':
            answer = {i : price_all[i][2]['A92']}
            answer_dict.update(answer)
        elif fuel_type == 'Diesel':
            answer = {i : price_all[i][3]['Diesel']}
            answer_dict.update(answer)
        elif fuel_type == 'GAS':
            if price_all[i][4]['GAS'] == '-':
                pass
            else:
                answer = {i : price_all[i][4]['GAS']}
                answer_dict.update(answer)
    
    answer_list = list(answer_dict.items())
    answer_list.sort(key=lambda i: i[1])
    return answer_list[::-1] #вывод значений в обратном порядке

@bot.message_handler(commands=['start'])
def btn(message):
    markup = types.ReplyKeyboardMarkup(row_width=5)
    a95i = types.KeyboardButton('A95+')
    a95 = types.KeyboardButton('A95')
    a92 = types.KeyboardButton('A92')
    diesel = types.KeyboardButton('Diesel')
    gas = types.KeyboardButton('GAS')
    select_area = types.KeyboardButton('/Выбрать_область')
    markup.add(a95i, a95, a92, diesel, gas, select_area)
    bot.send_message(message.chat.id, "Выберите тип топлива:", reply_markup=markup)

@bot.message_handler(commands=['Выбрать_область'])
def area_data(message):
    areas = ["Винницкая область", 
             "Волынская область", 
             "Днепропетровская область", 
             "Донецкая область",
             "Житомирская область",
             "Закарпатская область",
             "Запорожская область",
             "Ивано-Франковская",
             "Киевская область",
             "Кировоградская область",
             "Луганская область",
             "Львовская область",
             "Николаевкая область",
             "Одесская область",
             "Полтавская область",
             "Ровненская область",
             "Сумская область",
             "Тернопольская область",
             "Харьковская область",
             "Херсонская область",
             "Хмельницкая область",
             "Черкасская область",
             "Черниговская область",
             "Черновицкая область"]

    btn = types.InlineKeyboardMarkup()
    for i in areas:
        btn_areas = types.InlineKeyboardButton(text=i, callback_data=i)
        btn.add(btn_areas)    
    bot.send_message(message.chat.id, reply_markup = btn, text='Выберите область:')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "Винницкая область":
            azs_area_names = ['Chipo', 'Mango', 'Shell', 'SUN OIL', 'WOG', 'БРСМ-Нафта', 'OKKO', 'Укрнафта']
            create_fuel_buttons(call, azs_area_names)

def create_fuel_buttons(call, azs_area_names):
    fuel_btns = ['A95+', 'A95', 'A92', 'Diesel', 'GAS']
    btn = types.InlineKeyboardMarkup()
    for i in fuel_btns:
        btn_fuels = types.InlineKeyboardButton(text=i, callback_data=i)
        btn.add(btn_fuels)    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите тип топлива", reply_markup=btn)
    
    request(call, azs_area_names)

def request(call, azs_area_names):
    if call.message:
        if call.data == "A95":
            print(call.data)
            print(azs_area_names)
#     if call.message:
#         titles, fuel_costs = parse(URL)
#         azs_names = azs_titles(titles)
#         cost_list_all = costs(fuel_costs)
#         price_all = title_and_cost_group(azs_names, cost_list_all) 
#         answer_list = sort(call.data, azs_area_ames, price_all)
        
#         btn = types.InlineKeyboardMarkup()    
#         for i in answer_list:
#             btn_fuel = types.InlineKeyboardButton(text=f'{i[0]} - {i[1]} грн/л', url=f'https://www.google.com/maps/search/автозаправка+{i[0]}')
#             btn.add(btn_fuel)
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Актуальные цены на {call.data}", reply_markup=btn)



    # bot.send_message(message.chat.id, reply_markup = btn, text='Выберите тип топлива:')




@bot.message_handler(content_types=['text'])
def fuel(message):
    #Формируем кнопки
    # markup = types.ReplyKeyboardMarkup(row_width=5)
    # a95i = types.KeyboardButton('A95+')
    # a95 = types.KeyboardButton('A95')
    # a92 = types.KeyboardButton('A92')
    # diesel = types.KeyboardButton('Diesel')
    # gas = types.KeyboardButton('GAS')
    # select_area = types.KeyboardButton('/Выбрать_область')
    # markup.add(a95i, a95, a92, diesel, gas, select_area)
    
    #Формируем ответ
    titles, fuel_costs = parse(URL)
    azs_names = azs_titles(titles)
    cost_list_all = costs(fuel_costs)
    price_all = title_and_cost_group(azs_names, cost_list_all) 
    answer_list = sort(message.text, azs_names, price_all)
      
    btn = types.InlineKeyboardMarkup()    
    for i in answer_list:
        btn_fuel = types.InlineKeyboardButton(text=f'{i[0]} - {i[1]} грн/л', url=f'https://www.google.com/maps/search/автозаправка+{i[0]}')
        btn.add(btn_fuel)
    bot.send_message(message.chat.id, reply_markup = btn, text=f'Актуальные цены на {message.text}')

if __name__== "__main__":
    bot.polling(none_stop=True, timeout=999999)




