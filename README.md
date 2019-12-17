---
title: "README"
author: "Chukwubuikem Ume-Ugwa"
date: "December 16, 2019"
output:
  html_document: default
---

## Project structure

discussion-mapper<br/>
 ┣ 🗂api <br/>
 ┃ ┣ 🗂migrations<br/>
 ┃ ┃ ┗ 📄__ init__.py<br/>
 ┃ ┣ 📄__ init__.py<br/>
 ┃ ┣ 📄admin.py<br/>
 ┃ ┣ 📄apps.py<br/>
 ┃ ┣ 📄mapper.py<br/>
 ┃ ┣ 📄models.py<br/>
 ┃ ┣ 📄test.py<br/>
 ┃ ┣ 📄urls.py<br/>
 ┃ ┗ 📄views.py<br/>
 ┣ 🗂libs<br/>
 ┃ ┣ 📄__ init__.py<br/>
 ┃ ┣ 📄analyzers.py<br/>
 ┃ ┣ 📄base_crawler.py<br/>
 ┃ ┣ 📄database_api.py<br/>
 ┃ ┣ 📄db_loaders.py<br/>
 ┃ ┣ 📄graph_writers.py<br/>
 ┃ ┣ 📄json_models.py<br/>
 ┃ ┣ 📄main.py<br/>
 ┃ ┣ 📄mapper.py<br/>
 ┃ ┣ 📄models.py<br/>
 ┃ ┣ 📄mp_test.py<br/>
 ┃ ┣ 📄reddit_crawler.py<br/>
 ┃ ┣ 📄redditor_attributes.py<br/>
 ┃ ┗ 📄textsim.py<br/>
 ┣ 🗂main<br/>
 ┃ ┣ 🗂migrations<br/>
 ┃ ┃ ┗ 📄__ init__.py<br/>
 ┃ ┣ 🗂static<br/>
 ┃ ┃ ┗ 🗂main<br/>
 ┃ ┃ ┃ ┣ 🗂css<br/>
 ┃ ┃ ┃ ┃ ┗ 📄style.css<br/>
 ┃ ┃ ┃ ┗ 🗂js<br/>
 ┃ ┃ ┃ ┃ ┣ 📄event_handlers.js<br/>
 ┃ ┃ ┃ ┃ ┣ 📄jquery-3.3.1.min.js<br/>
 ┃ ┃ ┃ ┃ ┣ 📄loaders.js<br/>
 ┃ ┃ ┃ ┃ ┣ 📄main.js<br/>
 ┃ ┃ ┃ ┃ ┣ 📄mapper_module.js<br/>
 ┃ ┃ ┃ ┃ ┣ 📄render_main.js<br/>
 ┃ ┃ ┃ ┃ ┗ 📄render_mapper.js<br/>
 ┃ ┣ 🗂templates<br/>
 ┃ ┃ ┗ 🗂main<br/>
 ┃ ┃ ┃ ┣ 📄header.html<br/>
 ┃ ┃ ┃ ┗ 📄viz.html<br/>
 ┃ ┣ 📄__ init__.py<br/>
 ┃ ┣ 📄admin.py<br/>
 ┃ ┣ 📄apps.py<br/>
 ┃ ┣ 📄models.py<br/>
 ┃ ┣ 📄tests.py<br/>
 ┃ ┣ 📄urls.py<br/>
 ┃ ┗ 📄views.py<br/>
 ┣ 🗂mapper<br/>
 ┃ ┣ 📄__ init__.py<br/>
 ┃ ┣ 📄settings.py<br/>
 ┃ ┣ 📄urls.py<br/>
 ┃ ┗ 📄wsgi.py<br/>
 ┣ 🗂misc<br/>
 ┃ ┣ 🗂graphML<br/>
 ┃ ┣ 🗂images<br/>
 ┃ ┗ 🗂raw<br/>
 ┣ 🗂pictures<br/>
 ┣ 📄.gitignore<br/>
 ┣ 📄Dockerfile<br/>
 ┣ 📄docker-compose.yml<br/>
 ┣ 📄README.md<br/>
 ┣ 📄_config.yml<br/>
 ┣ 📄db.sqlite3<br/>
 ┣ 📄manage.py<br/>
 ┣ 📄requirements.txt<br/>
 ┗ 📄test.py<br/>
 
The mapper folder is where the Django project settings files live. There are two applications in the project, api and main. api is the backend support that implements mapper logic and provides endpoints to interact with mapper. main is the old front-end now replaced by [mapper_ui](https://github.com/CleverChuk/mapper_ui). libs/ contains modules used to scrape data from Reddit and load into neo4j

### Setup
#### Build docker image for backend
1. `Prerequisite`
    - download and install [docker](https://docs.docker.com/install/)
2. clone this repository
3. open a new terminal
4. cd into discussion-mapper/
5. run docker build -t [username]/[repository]:[tag] .

For the backend to communicate with the neo4j database you need to use docker-compose to start the whole system. See the `docker-compose.yml file`. You can modified the file to use the image you built.

#### Running the system
1. make sure you're in repository folder
2. run docker-compose up
3. browse to http://localhost:7474
4. when prompted enter neo4j for password
5. change password to neo4j2
6. cd into discussion-mapper/libs/
7. make sure that credential.json is in discussion-mapper/libs dir and contains your login for Reddit
```js
sample: credential.json file content
{
  "client_secret":"client secret",
  "client_id":"client id",
  "username": "username",
  "password":  "password"
}
```
8. run `python3 main.py` to start uploading data from reddit to neo4j
9. browse to http://localhost:3000
10. interact with the application
