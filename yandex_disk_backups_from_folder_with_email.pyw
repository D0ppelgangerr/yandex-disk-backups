import os
import hashlib
import yadisk
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Инициализация Яндекс.Диска
y = yadisk.YaDisk(token="my_token")

# Учетные данных отправителя
sender_email = "mail@email.com"
sender_password = "password"

# Конфигурация получателя
receiver_email = "mail@email.com"

# Путь к локальной папке и папке на Яндекс.Диске
local_folder_path = r'C:\Users\User\Desktop\files_for_backup'
yandex_folder_path = '/Backuped'


def calculate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()


def backup_files(local_folder, yandex_folder):
    digest = ''

    # Проверка существования папки Backuped на Яндекс.Диске
    if not y.exists(yandex_folder):
        y.mkdir(yandex_folder)

    for file_name in os.listdir(local_folder):
        local_file_path = os.path.join(local_folder, file_name)
        yandex_file_path = yandex_folder + '/' + file_name

        # Проверка существования файла на Яндекс.Диске
        if y.exists(yandex_file_path):
            # Сравнение хэшей
            local_file_hash = calculate_hash(local_file_path)
            yandex_file_hash = y.get_meta(yandex_file_path).md5

            if local_file_hash != yandex_file_hash:
                # Обновление файла на Яндекс.Диске
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                new_yandex_file_path = yandex_folder + '/' + timestamp + '_' + file_name
                y.upload(local_file_path, new_yandex_file_path)
                digest += f'Файл {file_name} обновлен. \n'
                print(f'Файл {file_name} обновлен. \n')
        else:
            # Загрузка файла на Яндекс.Диск
            y.upload(local_file_path, yandex_file_path)
            digest += f'Файл {file_name} загружен на Яндекс.Диск. \n'
            print(f'Файл {file_name} загружен на Яндекс.Диск. \n')

    if digest != '':
        # Создание объекта сообщения
        message = MIMEMultipart()
        message["Subject"] = "Создана/обновлена резервная копия на Яндекс.Диске"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Преобразование текста в MIMEText объект и добавление их в сообщение
        text = MIMEText(digest, "plain")
        message.attach(text)

        # Подключение к серверу и отправка сообщения
        try:
            server = smtplib.SMTP('smtp.yandex.ru', 587)  # Используйте правильный SMTP сервер и порт
            server.starttls()  # Старт безопасного соединения
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            print("Email успешно отправлен!")
        except Exception as e:
            print(f"Ошибка при отправке email: {e}")


backup_files(local_folder_path, yandex_folder_path)
