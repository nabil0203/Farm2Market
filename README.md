# Farm2Market

## Setup Instructions

1. Clone & pull code
```bash
git pull
```

2. Create & activate virtual environment (if needed)
```bash
py -m venv my_env
```

3. Install dependencies (in the same directory as manage.py)
```bash
py -m pip install -r requirements.txt
```

4. Download the media folder from: https://drive.google.com/drive/folders/1gz0SvMe0pYM71-PdeljfQt_BYKn3_1tH
In the project, Move the "media" folder in the same directory as manage.py

5. Create .env (in the same directory as manage.py)


6. Install PostgreSQL drivers (if missing)
```bash
pip install psycopg2-binary dj-database-url python-dotenv
```

7. Run migrations
```bash
# If models unchanged:
python manage.py migrate

# If models changed:
python manage.py makemigrations
python manage.py migrate
```

8. Create superuser
```bash
python manage.py createsuperuser
```

9. Run server
```bash
python manage.py runserver
```
