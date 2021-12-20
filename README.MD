# django-setup-cli

#### Django Setup Cli
[![GitHub Actions (Tests)](https://github.com/khan-asfi-reza/django-setup-cli/workflows/Build/badge.svg)](https://github.com/khan-asfi-reza/django-cli)
[![codecov](https://codecov.io/gh/khan-asfi-reza/django-setup-cli/branch/master/graph/badge.svg?token=GRFSIFESKQ)](https://codecov.io/gh/khan-asfi-reza/django-setup-cli)

It takes time to start a Django Project and make it almost production ready. A developer needs to spend a lot of time 
installing required libraries, setup database, setup cache as well as hiding secrets, configure `settings` file.
With the help of `django-setup-cli` a developer can start an `almost production ready` project in a minute.

### Requirements
`python 3.6>`

## Installation
### 1. Create a virtual environment and activate

`windows`
```cmd
 pip install virtualenv
 virtualenv venv
 <YOUR WORKING DIRECTORY>/venv/scripts/activate
```
>Your Current Working Directory

`Ubuntu [Debian]`
```commandline
sudo apt-get install python3-pip
sudo pip3 install virtualenv 
virtualenv venv 
source venv/bin/activate
```
>you can use any name instead of **venv**
### 2. Install django-setup-cli
```cmd
pip3 install django-setup-cli
```

## Usages

`How to use`
```cmd
Usage: django-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  generate      Generates YAML File
  startproject  Starts Django Project

```


###  1. `startproject`
###  Option 1:
Similar to `django-admin startproject`

If there's no valid `setup.yaml` file in your working directory
django-cli will take some input to start the project

To Start a project use the following command in the shell

> django-cli startproject PROJECT_NAME

`Note: PROJECT_NAME is optional`

```command
>> django-cli startproject ProjectName[Optional]

1. Project Name
Your Project Name: T

2. Install Necessary Libraries
Install Libraries [y/N]: y

1.Install djangorestframework [y/N]: y
2.Install graphene-django [y/N]: y
3.Install django-channels [y/N]: y
4.Install django-localflavor [y/N]: y
5.Install celery [y/N]: y
6.Install whitenoise [y/N]: y
7.Install django-filter [y/N]: y
8.Install django-extensions [y/N]: y
9.Install django-storages [y/N]: y

3. Static File
Create/Use Static File [y/N]: y

4. Template File
Create/Use Template File [y/N]: y

5. Media File
Create/Use Media File [y/N]: y

6. Setup Database
Setup Database [Skip To Use Default] [y/N]: y
1. postgresql
2. mysql
3. maria_db
4. oracle
5. mssql
6. sqlite3
7. django_cockroachdb

Database Engine: 1
Database Name: DATABASE_NAME
Database User: USER
Database Password: PASSWORD
Database Host: localhost
Database Port: 5432

7. Setup Cache
Install Cache [y/N]: y

1. pymemcache
2. redis
3. DatabaseCache
4. FileBasedCache
5. LocMemCache

Cache Engine: 2
Cache Location: LOCATION

```
After Providing required Information Your Project will be created and you will see following output
```
1. Installing Required Libraries
installing django
...
...
2. Creating Source Directory
..
3. Creating Project File

Project Setup Complete
```

Your working directory will have the following files and folders
```
project
│   README.md
│   .gitignore    
│   .env       [Django Secrets]
|   setup.yaml [django-cli YAML Setup Config File]  
└───src
   │   manage.py
   │   
   └───PROJECT_NAME
       │   asgi.py
       │   config.py
       │   settings.py   
       |   wsgi.py
       |   urls.py 

```

> Note: Do not delete `.env` file, it will contain database, cache and django secret keys

### Option 2:

#### 1. Create a `setup.yaml` file
```yaml
name: TEST_PROJECT
libraries:
- django-rest-framework
- celery
- django-storages
template: true
static: true
media: false
database:
  engine: postgresql
  user: user
  password: password
  host: host
  port: port
  option: 
    config: psql.cfg
cache:
  backend: redis
  location: localhost:6532
env:
  SECRET_KEY: YOUR_SECRET_KEY

```

#### 2. Run `django-cli startproject` in terminal/shell

```cmd
django-cli startproject
# Your Project Will be created automatically using the setup.yaml file
```

#### Use Environment Variable in `setup.yaml`

> It is possible to use secrets I.E [Database Password, Username, Secret Key] using environment variable

To Hide Secrets Using `environment variable` create a `cli.env` file in the source directory
And do the following

`cli.env`
```dotenv
MY_SECRET_KEY=<YOUR_SECRET_KEY>
DATABASE_USER=django_cli
DATABASE_PASSWORD=gonnaCry?
```
`setup.yaml`

To use env secret Put `$` before your env variable
I.E `$SECRET_KEY`

```yaml
name: TEST_PROJECT
libraries:
- django-rest-framework
- celery
- django-storages
template: true
static: true
media: false
database:
  engine: postgresql
  user: $DATABASE_USER
  password: $DATABASE_PASSWORD
  host: host
  port: port
  option: 
    config: psql.cfg
cache:
  backend: redis
  location: localhost:6532
env:
  SECRET_KEY: $MY_SECRET_KEY
```

> You can target a different env file using `--env`
> `django-cli startproject NewProject --env spider.env`


###  2. `generate`

```commandline
django-cli generate PROJECT_NAME --env cli.env
```
Will generate `setup.yaml` file, it will not create project
`PROJECT_NAME` and `--env` are optional fields
### 3. `install`

```commandline
django-cli install
```

Will install required libraries also install libraries that are inside `requirements.txt` file


@Creator and Maintainer

Khan Asfi Reza