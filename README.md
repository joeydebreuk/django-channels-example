#### Django channels:

- django version 2.2
- channels version 2.4
- run websockets server with Daphne

#### To deploy:

Set environment variables `CHANNELS_REDIS_IP` and `CHANNELS_REDIS_PORT`

#### How to run it local:

`pip install -r requirements.txt`

`python manage.py migrate`

`python manage.py runserver 0:8000`

Run ASGI app in new console:

`daphne -p 8001 websockets.ws_application:application`

Run Redis in new console:

`docker run -p 6379:6379 redis:5`

Go to https://localhost:8000/
