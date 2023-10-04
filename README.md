# FastApi Backend online store

### For start app in local:

Python 3.10.11

Clone repository from git.... Use branch master.

1. Install Poetry.

   use command `pip install poetry`

2. Create poetry environment 

   use command `poetry install`

3. Activate poetry environment 

   use command `poetry shell`

4. Create file .env in /. End record the value from example_env.txt

5. Install Docker-Compose ... and -->

   use command `docker-compose up -d`

6. Create DB

   use command `alembic upgrade head`

7. Start app FastApi

   use command `uvicorn main:app --host localhost --port 8000 --reload`

8. use command to write logs to a file `uvicorn main:app --log-level info --host localhost --port 8000 --log-config src/conf/logging_config.ini`



### Insert test data into database 

""" At first, you need to create a file called `test_users_data.py` with users data(email, password, role) 
using the schema in a file called `test_users_data.sample.py`. """
