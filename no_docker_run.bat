:: Create virtual env
if not exist pharm-env ( python -m pharm-env )

:: Activate virtual env
pharm-env\Scripts\activate 

:: Install dependencies
pip install -r requirements.txt

:: Make migrations 
python manage.py makemigrations

:: Apply migrations
python manage.py migrate

:: Start development server on port 8000
python manage.py migrate

echo "Hosting address: http://127.0.0.1:8000/ has been copied to clipboard"
echo "Paste it on a browser. Enjoy  development!"
clip < echo http://127.0.0.1:8000/
pause 
