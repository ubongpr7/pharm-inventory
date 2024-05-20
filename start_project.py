import os 
import subprocess

# if not os.path.exists('pharm-env'):
#     print('pharm-env is being created')
#     subprocess.run(f"python -m venv pharm-env",shell=True)

# else:
#     print('pharm-env already exists')
# subprocess.run(rf"pharm-env\Scripts\activate",shell=True)

subprocess.run(rf"pip install -r requirements.txt",shell=True)

subprocess.run(rf"python manage.py makemigrations",shell=True)
subprocess.run(rf"python manage.py migrate",shell=True)
subprocess.run(rf"python manage.py runserver",shell=True)

print('you can view the website via http://127.0.0.1:8000/')