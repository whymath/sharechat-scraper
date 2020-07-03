## Introduction

The keyword filter pipeline passes multilingual and multimodal social media / chat app content archived by Tattle through a data pipeline comprising of a series of Luigi tasks. When triggered, it executes all the tasks and adds a binary label to each item's Mongo DB record depending on whether it contains some defined keywords. These keywords are topic words extracted via LDA topic modelling on Tattle's database of fact-checking stories. The purpose of this pipeline is to flag content that is more relevant, i.e. more likely to contain misinformation.
Read more about Luigi pipelines [here](https://luigi.readthedocs.io/en/stable/index.html)

## Running locally

1. Fork the repo 
2. Create a new virtual environment and install the dependencies 
```
pip install requirements.txt
```
3. Create a .env file with Mongo DB and Google Vision API credentials
```
export DB_NAME = <>
export DB_PASSWORD = <>
export DB_COLLECTION = <>
export GOOGLE_APPLICATION_CREDENTIALS = <>
```
4. Activate the task visualizer. Command line:
```
luigid --background --pidfile ./luigid.pid --logdir luigi --state-path luigi/state --address 0.0.0.0 --port 8082
```
5. Open localhost:8082 in a browser window to monitor the tasks
6. Trigger the pipeline. Command line:
```
python3 -m luigi --module keyword_filter_pipeline StoreLabel --db <mongo_database_name> --collection <collection_name> --field "keyword_filter"
``` 