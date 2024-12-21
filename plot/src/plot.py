import pandas as pd
import matplotlib.pyplot as plt
import time
from pathlib import Path
import seaborn as sns

# Путь к файлу логов
log_file = Path('./logs/metric_log.csv')
output_image = Path('./logs/error_distribution.png')

while True:
    try:
        # Проверяем, существует ли файл логов
        if log_file.exists():
            # Загружаем данные
            data = pd.read_csv(log_file)
            # Строим гистограмму абсолютных ошибок
            plt.figure()
            sns.histplot(data['absolute_error'], bins=10, kde=True, color='orange', edgecolor='black', alpha=0.7)
            plt.title('Распределение абсолютных ошибок')
            plt.xlabel('absolute_error')
            plt.ylabel('Частота')
            plt.savefig(output_image)
            plt.close()
            print(f'Гистограмма обновлена: {output_image}')
        else:
            print('Файл логов не найден. Ожидание...')
        time.sleep(5)  # Ожидание перед обновлением
    except Exception as e:
        print(f'Ошибка при построении графика: {e}')