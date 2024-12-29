#  Проект «Foodgram - Продуктовый помощник»  
  
    
## Описание проекта:    
    
«Фудграм» — сайт, на котором пользователи могут:  
- Публиковать рецепты,  
- Добавлять чужие рецепты в избранное  
- Подписываться на публикации других авторов.

> Это одностраничное SPA-приложение. Написал с нуля бэкенд и REST API строго в соответствии со спецификацией. Спроектировал базу дынных, настроил админку, реализовал импорт тестовых данных в БД. Реализовал сервис для формирования списка покупок и последующего его скачивания (текстовый файл). Настроил инфраструктуру: запуск проекта в контейнерах, автоматическое тестирование и деплой проекта на удалённый сервер (CI/CD).
  
##### Сервис «Список покупок»  
Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.  
    

## Как развернуть проект локально  
  
Клонировать репозиторий и перейти в него в командной строке:    
    
```  
git clone https://github.com/andrey-kobelev/foodgram-project-react.git  
```    
    
```  
cd foodgram-project-react 
```    
    
Cоздать и активировать виртуальное окружение:    
    
```  
python3 -m venv venv  
```    
    
```  
source venv/bin/activate  
```    
    
Установить зависимости из файла requirements.txt:    
    
```  
python3 -m pip install --upgrade pip  
```    
    
```  
pip install -r requirements
```    
    
Выполнить миграции:    

```  
cd backend
``` 
    
```  
python3 manage.py migrate 
```  

Импортировать в БД данные для работы приложения. Выполняйте команды поочередно (import-recipes в самом конце!!!):

```
python3 manage.py import-ingredients
python3 manage.py import-tags
python3 manage.py import-users
python3 manage.py import-recipes
```
    
Запустить проект:    
    
```  
python3 manage.py runserver  
```    

После запуска будет доступен интерфейс для тестирования API по ссылке: http://127.0.0.1:8000/api/

## Запустить проект с фронтом локально

Файл `.env`, для локального запуска должен быть таким и находиться в корневой директории проекта:

```
POSTGRES_USER=django_user  
POSTGRES_PASSWORD=123456789django  
POSTGRES_DB=django_food
DB_HOST=foodgram_db  
DB_PORT=5432  
SECRET_KEY=<django_secret_key_from_settings> 
ALLOWED_HOSTS=<domain>,<server_ip>,127.0.0.1,localhost,0.0.0.0  
DEBUG_VALUE=True  
SQLITE=True
```

Далее в корневой директории выполните команду:

```
sudo docker compose -f docker-compose.yml up -d --build
```

> В проекте два файла docker compose: один для продакшена другой для локального запуска. `docker-compose.yml` - для локального запуска.

Далее поочередно выполните следующие команды так же находясь в корневой директории проекта:

```
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Импортировать данные в БД:

```
sudo docker compose -f docker-compose.yml exec backend python manage.py import-ingredients
sudo docker compose -f docker-compose.yml exec backend python manage.py import-tags
sudo docker compose -f docker-compose.yml exec backend python manage.py import-users
sudo docker compose -f docker-compose.yml exec backend python manage.py import-recipes
```

Чтобы остановить контейнеры:

```
sudo docker compose -f docker-compose.yml down
```


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
# DB_HOST=db  # DB_PORT=5432  
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
  
  # Сохраняем изменения и выходим из редактора  # Проверяем корректность настроек  sudo nginx -t  # Запускаем NGINX  sudo systemctl start nginx    
```    
##### Настраиваем HTTPS  (после того как получите доменное имя)  
    
```bash  
# Установка пакетного менеджера snap.  
# У этого пакетного менеджера есть нужный вам пакет — certbot.  
sudo apt install snapd  
# Установка и обновление зависимостей для пакетного менеджера snap.  
sudo snap install core 
sudo snap refresh core  
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


### Над проектом работал:    
* [Kobelev Andrey](https://github.com/andrey-kobelev)
