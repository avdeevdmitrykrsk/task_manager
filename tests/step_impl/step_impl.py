from http import HTTPStatus

import requests
from getgauge.python import after_scenario, before_scenario, data_store, step

BASE_URL = 'http://localhost:8000/api/tasks'


@before_scenario
def setup():
    data_store.scenario['tasks'] = []
    data_store.scenario['last_response'] = None


@after_scenario
def teardown():
    tasks = data_store.scenario.get('tasks')
    try:
        for task in tasks:
            requests.delete(f'{BASE_URL}/{task["id"]}')
    except:  # noqa
        pass


@step('Создать задачу <name>')
def create_task(name):
    payload = {
        'name': name,
        'description': f'Тестовое описание для {name}',
    }

    response = requests.post(f'{BASE_URL}', json=payload)
    response.raise_for_status()

    task = response.json()
    data_store.scenario['tasks'].append(task)
    data_store.scenario['last_response'] = response
    return task


@step('Убедиться что созданная ранее задача существует')
def get_task():
    last_task = data_store.scenario.get('tasks')[-1]
    task_id = last_task['id']

    response = requests.get(f'{BASE_URL}/{task_id}')
    response.raise_for_status()

    actual_task = response.json()
    assert actual_task['id'] == task_id, 'ID задачи не совпадает'
    assert (
        actual_task['name'] == last_task['name']
    ), 'Название задачи не совпадает'

    data_store.scenario['last_response'] = response


@step('Обновить у задачи имя на <new_name>')
def update_task_name(new_name):
    last_task = data_store.scenario.get('tasks')[-1]
    task_id = last_task['id']

    payload = {'name': new_name}

    response = requests.patch(f'{BASE_URL}/{task_id}', json=payload)
    response.raise_for_status()

    actual_task = response.json()
    assert actual_task['name'] == new_name

    data_store.scenario['last_response'] = response


@step('Удалить задачу')
def delete_task():
    last_task = data_store.scenario.get('tasks')[-1]
    task_id = last_task['id']

    response = requests.delete(f'{BASE_URL}/{task_id}')

    assert response.status_code == HTTPStatus.NO_CONTENT

    data_store.scenario['last_response'] = response
