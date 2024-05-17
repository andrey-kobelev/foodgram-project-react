#  Проект «Foodgram - Продуктовый помощник»

![status](https://github.com/andrey-kobelev/foodgram-project-react/actions/workflows/main.yml/badge.svg)
  
## Описание проекта:  
  
«Фудграм» — сайт, на котором пользователи могут:
- Публиковать рецепты,
- Добавлять чужие рецепты в избранное
- Подписываться на публикации других авторов. 

##### Сервис «Список покупок»
Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
  

## Как запустить проект на удаленном сервере:  
##### Настраиваем Docker

```bash
sudo apt update  
sudo apt install curl  
curl -fSL https://get.docker.com -o get-docker.sh  
sudo sh ./get-docker.sh  
sudo apt-get install docker-compose-plugin;  
# Переходим в директорию проекта.  
cd foodgram/
# Директория долдна содержать файл docker-compose.production.yml
# Создаем и редактируем файл .env, в котором нужно указать данные  
sudo nano .env  
# DJANGO_KEY=<секретный_ключ_django>
# POSTGRES_DB=<Желаемое_имя_базы_данных>  
# POSTGRES_USER=<Желаемое_имя_пользователя_базы_данных>  
# POSTGRES_PASSWORD=<Желаемый_пароль_пользователя_базы_данных>  
# DB_HOST=db  
# DB_PORT=5432  
# Сохраняем файл.
# Далее выполняем последовательно  
sudo docker compose -f docker-compose.production.yml pull  
sudo docker compose -f docker-compose.production.yml down  
sudo docker compose -f docker-compose.production.yml up -d  
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate  
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic  
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collect_static/. /static_backend/static/ 
```  

##### Наполнить БД необходимыми данными (теги, ингредиенты, пользователи и рецепты)

```bash
# После того как миграции пройдут успешно, импортируйте данные в БД введя команды (import-recipes в самом конце!!!):
	# ..manage.py import-ingredients
	# ..manage.py import-tags

sudo docker compose -f docker-compose.production.yml exec backend python manage.py import-ingredients
# После успешного наполнения БД данными вы увидете примерно такое сообщение:

Начало импорта ингредиентов... (ok)

Импорт ингредиентов выполнен успешно
```

##### Устанавливаем и настраиваем NGINX  
  
```bash  
# Устанавливаем NGINX  
sudo apt install nginx -y  
# Запускаем  
sudo systemctl start nginx  
# Настраиваем firewall  
sudo ufw allow 'Nginx Full'  
sudo ufw allow OpenSSH  
# Включаем firewall  
sudo ufw enable  
# Открываем конфигурационный файл NGINX  
sudo nano /etc/nginx/sites-enabled/default  
# Добавьте новые настройки  

# server {
#    server_name 51.250.97.96;
#    server_tokens off;

#    location / {
#        proxy_set_header Host $http_host;
#        proxy_pass http://127.0.0.1:9080;
#    }
#}

  
# Сохраняем изменения и выходим из редактора  
# Проверяем корректность настроек  
sudo nginx -t  
# Запускаем NGINX  
sudo systemctl start nginx  
```  

##### Настраиваем HTTPS  (после того как получите доменное имя)
  
```bash  
# Установка пакетного менеджера snap.  
# У этого пакетного менеджера есть нужный вам пакет — certbot.  
sudo apt install snapd  
# Установка и обновление зависимостей для пакетного менеджера snap.  
sudo snap install core; sudo snap refresh core  
# При успешной установке зависимостей в терминале выведется:  
# core 16-2.58.2 from Canonical✓ installed   
# Установка пакета certbot.  
sudo snap install --classic certbot  
# При успешной установке пакета в терминале выведется:  
# certbot 2.3.0 from Certbot Project (certbot-eff✓) installed  
  
# Создание ссылки на certbot в системной директории,  
# чтобы у пользователя с правами администратора был доступ к этому пакету.  
sudo ln -s /snap/bin/certbot /usr/bin/certbot  
  
# Получаем сертификат и настраиваем NGINX следуя инструкциям  
sudo certbot --nginx  
# Перезапускаем NGINX  
sudo systemctl reload nginx  
```  

## Как запустить проект локально

### Файл `docker-compose.yml`
Что бы запустить проект локально, ваш `docker-compose.yml` файл должен выглядеть так:

```yaml
volumes:  
  pg_data:  
  static:  
  media:  
  
services:  
  db:  
    image: postgres:13  
    env_file: ./.env  
    container_name: foodgram_db  
    volumes:  
      - pg_data:/var/lib/postgresql/data  
  backend:  
    build: ./backend/  
    env_file: ./.env  
    depends_on:  
      - db  
    volumes:  
      - media:/app/media  
      - static:/backend_static  
  frontend:  
    build: ./frontend/
    env_file: ./.env  
    command: cp -r /app/build/. /frontend_static/  
    volumes:  
      - static:/frontend_static  
  gateway:  
    build: ./infra/
    env_file: ./.env  
    ports:  
      - 8000:80  
    volumes:  
      - static:/staticfiles  
      - media:/media
```

Проверьте файл `.env`, убедитесь что там есть все необходимые переменные

```bash
POSTGRES_USER=<user>  
POSTGRES_PASSWORD=<password>  
POSTGRES_DB=<db-name>  
DB_HOST=<db_container_name>  
DB_PORT=<port>  
SECRET_KEY=<django_key>  
ALLOWED_HOSTS=<localhost_ip>,<localhost>
DEBUG_VALUE=<True or False>

# Для локального запуска контейнеров,
# установите False
SQLITE=<True or False>
```

Далее выполните последовательно команды находясь в директории проекта:

```bash
sudo docker compose -f docker-compose.yml up -d
sudo docker compose -f docker-compose.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate  
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic  
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collect_static/. /static_backend/static/
```

Что-бы остановить работу контейнеров:

```bash
sudo docker compose -f docker-compose.yml down
```

--- 

## В проекте были использованы технологии:  
* #### [Django REST](https://www.django-rest-framework.org/)  
* #### [ Python 3.9](https://www.python.org/downloads/release/python-390/)
* #### [Gunicorn](https://gunicorn.org/)
* #### [Nginx](https://www.nginx.com/)
* #### [JS]()
* #### [Node.js](https://nodejs.org/en)
* #### [PostgreSQL](https://www.postgresql.org/)
* #### [Docker](https://www.docker.com/)
* #### [React](https://ru.legacy.reactjs.org/)
---  
### Над проектом работал:  
* [Kobelev Andrey](https://github.com/andrey-kobelev)