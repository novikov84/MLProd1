import pika
import json
import pandas as pd
from pathlib import Path
import time

# Задержка для ожидания готовности RabbitMQ при старте
time.sleep(1)

# Инициализация файла для логирования
log_file = Path('./logs/metric_log.csv')
log_file.parent.mkdir(parents=True, exist_ok=True)
if not log_file.exists():
    with open(log_file, 'w') as f:
        f.write('id,y_true,y_pred,absolute_error\n')

# Словари для хранения данных
received_y_true = {}
received_y_pred = {}

def calculate_and_log():
    # Совмещаем данные из двух очередей по ID
    common_ids = set(received_y_true.keys()) & set(received_y_pred.keys())
    for message_id in common_ids:
        y_true = received_y_true.pop(message_id)
        y_pred = received_y_pred.pop(message_id)
        absolute_error = abs(y_true - y_pred)
        # Логирование в файл
        with open(log_file, 'a') as f:
            f.write(f'{message_id},{y_true},{y_pred},{absolute_error}\n')
        print(f'Логировано: ID={message_id}, y_true={y_true}, y_pred={y_pred}, absolute_error={absolute_error}')
 
try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
   
    # Объявляем очередь y_true
    channel.queue_declare(queue='y_true')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')
 
    # Создаём функции callback для обработки данных из очередей
    def callback_y_true(ch, method, properties, body):
        message = json.loads(body)
        print(f'Получено y_true с ID {message["id"]}: {message["body"]}')
        received_y_true[message['id']] = message['body']
        calculate_and_log()

    def callback_y_pred(ch, method, properties, body):
        message = json.loads(body)
        print(f'Получено y_pred с ID {message["id"]}: {message["body"]}')
        received_y_pred[message['id']] = message['body']
        calculate_and_log()
 
    # Подписываемся на очереди
    channel.basic_consume(
        queue='y_true',
        on_message_callback=callback_y_true,
        auto_ack=True
    )
    channel.basic_consume(
        queue='y_pred',
        on_message_callback=callback_y_pred,
        auto_ack=True
    )
 
    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except Exception as e:
    print(f'Не удалось подключиться к очереди: {e}')
