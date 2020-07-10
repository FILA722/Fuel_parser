import requests
from bs4 import BeautifulSoup

URL = 'https://finance.i.ua/fuel/'
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 'accept': '*/*'}

cost_dict = {}
cost_list = []

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_content(html, fuel_type):
    soup = BeautifulSoup(html, 'html.parser')    
    news = soup.find_all('tr')
    
    for new in news:
        try:
            if fuel_type == 'dp':
                title = new.find('th', class_='td-title').get_text(strip=True)
                fuel_cost = new.find('td', class_='dp').get_text(strip=True)
            else:
                title = new.find('th', class_='td-title').get_text(strip=True)
                fuel_cost = new.find('td', class_=f'{fuel_type[0]}_{fuel_type[1:3]}').get_text(strip=True)

            cost={fuel_cost:title}
            cost_dict.update(cost)
            cost_list.append(fuel_cost)
        except AttributeError:
            pass

def sort(cost_list):
    key = True
    while key:
        key = False
        for j in range(len(cost_list)-1):
            if cost_list[j] > cost_list[j+1]:
                cost_list[j], cost_list[j+1] = cost_list[j+1], cost_list[j]
                key = True

def parse(fuel_type):
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text, fuel_type)
    else:
        print('Error')

fuel_type = input("choose your fuel type (a92, a95, dp): ")
parse(fuel_type)
sort(cost_list)

for i in cost_list:
    print (f'{cost_dict[i]} - {i} грн/л')
