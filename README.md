# Django start template

Django quick start template

## ENVIRONMENT

#### Copy and Configure env with project settings

```
cp .env.example .env
cp config/local_settings.example.py config/local_settings.py
```

## SetUp with virtualenv

```
python -m virtualenv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
