from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_CONFIG={'port' : os.environ.get('DATABASE_PORT', ''),
'host' : os.environ.get('DATABASE_HOST', ''),
'password' : os.environ.get('DATABASE_PASSWORD', ''),
'user' : os.environ.get('DATABASE_USER', ''),
'name' : os.environ.get('DATABASE_NAME', ''),
'engine' : os.environ.get('DATABASE_ENGINE', ''),
}
SECRET_KEY = os.environ.get('SECRET_KEY', '')
