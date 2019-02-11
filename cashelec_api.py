import requests
from datetime import datetime

# Устанавливаем параметры API и URL
params = {'CMC_PRO_API_KEY': '<API KEY GOES HERE>',
            'limit': 10,
            'sort': 'volume_24h'}
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'


def test_api(url, params):
    '''
    Функция принимает 2 аргумента:
    1. URL, к которому выполняем запрос
    2. Параметры запроса в виде словаря {'параметр':'значение'}
    Возвращает "True", если выполнены следующие условия:
    1. latency < 500ms
    2. полученная информация актуальна (обновлялась в день выполнения запроса)
    3. размер полученных данных < 10kb
    '''
    response = requests.get(url, params=params)
    data = response.json()
    latency = round(response.elapsed.total_seconds(),3)
    size_kb = len(response.content)//1024.0
    try:
        datetime_object = datetime.strptime(f'{data["data"][1]["last_updated"]}', '%Y-%m-%dT%H:%M:%S.000Z')
    except KeyError:
        return "Ошибка сервера. Данные не получены"
    if latency > 0.5:
        return f'Test failed. Latency: {latency}s'
    elif size_kb > 10:
        return f'Test failed. Packet size: {size_kb}kb'
    elif datetime_object.day != datetime.now().day:
        return f'Test failed. information is outdated'
    else:
        return True

if __name__=='__main__':
    print(test_api(url, params))
