import requests
import time
from numpy import percentile
from datetime import datetime
from multiprocessing import Process, Manager


# Устанавливаем параметры API и URL
params = {'CMC_PRO_API_KEY': '<API KEY GOES HERE>',
          'limit': 10,
          'sort': 'volume_24h'}
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

def test_api(url, params, pid, results_dict, latency_dict):
    '''
    Функция принимает 5 аргументов:
    1. URL, к которому выполняем запрос
    2. Параметры запроса в виде словаря {'параметр':'значение'}
    3. ID процесса
    4. словарь результатов
    5. словарь latency
    Записывает результаты теста в словарь results_dict, True или False:
    1. latency < 500ms
    2. полученная информация актуальна (обновлялась в день выполнения запроса)
    3. размер полученных данных < 10kb
    Записывает время выполнения запроса в словарь latency_dict
    Возвращает 0, если выполнена успешно.
    '''
    response = requests.get(url, params=params)
    data = response.json()
    latency = round(response.elapsed.total_seconds(),3)
    size_kb = len(response.content)//1024.0
    try:
        datetime_object = datetime.strptime(f'{data["data"][1]["last_updated"]}', '%Y-%m-%dT%H:%M:%S.000Z')
    except KeyError:
        results_dict[pid] = False
        return "Ошибка сервера. Данные не получены"
    results_dict[pid] = latency < 0.5 and datetime_object.day == datetime.now().day and \
                        size_kb <= 10
    latency_dict[pid] = latency
    return 0


def test_multiple_requests(results_dict, latency_dict):
    '''
    Анализирует результаты выполнения нескольких запросов одновременно
    Принимает 2 аргумента:
    1. Словарь результатов выполнения тестов
    2. Словарь latency выполненных тестов
    Возвращает True, если:
    1. Все экземпляры теста выполнены успешно
    2. 80 процентиль latency < 450ms
    3. rps > 5
    '''
    if False not in results_dict.values():
        # рассчитываем 80 процентиль latency
        percentile80 = percentile(latency_dict.values(), 80)
        # рассчитываем rps
        average_response_time = script_time/8
        if percentile80  >= 0.450:
            return f'Test failed. Latency percentile: {round(percentile80,3)}'
        elif average_response_time >= 0.2:
            return f'Test failed. rps: {round(1/average_response_time,1)}'
        else:
            return True
    else:
        return f'Test {(list(results_dict.keys())[list(results_dict.values()).index(False)])} failed'

if __name__=='__main__':
    # Создаем словари для записи результатов тестов
    manager = Manager()
    results_dict = manager.dict()
    latency_dict = manager.dict()
    list_of_processes = []
    script_start = time.time()
    # Создаем процесс для каждого экземпляра теста
    for pid in range(8):
        list_of_processes.append(Process(target=test_api, args=(url,
                                                                params,
                                                                str(pid),
                                                                results_dict,
                                                                latency_dict)))
        list_of_processes[pid].start()
    for pid in range(8):
        list_of_processes[pid].join()
    # запоминаем время выполнения тестов
    script_time = round(time.time() - script_start, 2)
    # выполняем функцию, анализарующую результаты тестов
    print(test_multiple_requests(results_dict, latency_dict))
