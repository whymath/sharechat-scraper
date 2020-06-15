# Introduction

This repository contains code for scraping publicly available data from targeted content tags on the Indian social network https://sharechat.com/

![Sharechat Content Tree](sharechat_content_tree.png)

# Why are we scraping this data?

One of Tattle's key goals is to create new knowledge around misinformation/disinformation on social media in India. To this end, we're creating an open archive of relevant multilingual content circulated on chat apps and social networks such as Sharechat. Read more about our goals and values here - https://tattle.co.in/faq

# Running locally

1. Create an account on Sharechat
2. Fork the repository 
3. Install required Python packages: `pip install requirements.txt`
4. Set up an AWS S3 bucket to store the scraped content (images, videos, text) and a MongoDB to store the scraped metadata (timestamps, likes, shares etc.)\
If you can't set up a MongoDB or S3 bucket, set the "mode" to "local" in the Config file (see no. 6)
5. Create a .env file in the same folder and save your Sharechat, MongoDB and S3 access credentials in the .env file. These should be in the following format:

   ```
   SHARECHAT_DB_USERNAME = <YOUR_MONGODB_USERNAME>
   SHARECHAT_DB_NAME = <YOUR_MONGODB_NAME>
   SHARECHAT_DB_PASSWORD = <YOUR_MONGODB_PASSWORD>
   SHARECHAT_DB_COLLECTION = <YOUR_MONGODB_COLLECTION>
   AWS_ACCESS_KEY_ID = <YOUR_AWS_ACCESS_KEY>
   AWS_SECRET_ACCESS_KEY_ID = <YOUR_AWS_SECRET_ACCESS_KEY>
   AWS_BUCKET = <YOUR_AWS_BUCKET>
   AWS_BASE_URL = <YOUR_AWS_BASE_URL>
   SHARECHAT_USER_ID = <YOUR_SHARECHAT_USER_ID>
   SHARECHAT_PASSWORD = <YOUR_SHARECHAT_PASSWORD>
   ```
6. Modify the Config file as per your requirements, then run it to start scraping: `python run config.py`

## Modifying the Config file

[config.py](config.py) is the only script you need to run to start scraping. It contains a dictionary named scraper_params. Depending on the values entered in this dictionary, the [Sharechat Manager](docs/sharechat_scraper_manager.md) called by Config will run one of the following scrapers - 

[Sharechat trending content scraper](docs/sharechat_trending_content_scraper.md)

[Sharechat fresh content scraper](docs/sharechat_fresh_content_scraper.md)   

[Sharechat ML scraper](docs/sharechat_ml_scraper.md) 

[Sharechat virality scraper](docs/sharechat_virality_scraper.md) (development stage)

**Usage**: Enter values in the scraper_params dictionary as per the scraping requirement, then run the file.

scraper_params takes the following key:value pairs -

* "USER_ID": os.environ.get("SHARECHAT_USER_ID") 
* "PASSCODE": os.environ.get("SHARECHAT_PASSCODE")\
  These two key:value pairs are required by all the scrapers in order to send requests to the Sharechat API. Your user id and passcode may unfortunately not be very obvious, but instructions for finding them are given below. 
* "tag_hashes": <tag_hashes_passed_as_list_of_strings>\
  Tag hashes are identifiers for content tags. These must be selected after a manual inspection of tags on Sharechat. Instructions for finding tag hashes are given below. 
* "bucket_ids": <bucket_ids_passed_as_list_of_strings>\
  Bucket ids are identifiers for content buckets. These must be selected after a manual inspection of content buckets on Sharechat. Instructions for finding bucket ids are given below. 
* "content_to_scrape": <string_value>\
  This value determines which scraper will be launched by the scraper manager. Possible values are "trending", "fresh", "ml" and "virality"
* "pages": <integer_value>\
  Number of pages to scrape. One page typically contains 10 posts. This is a required value when content_to_scrape = "trending" or "fresh" or "ml". This number should be kept reasonably low to avoid bombarding the Sharechat API with requests.
* "unix_timestamp": <10_digit_unix_timestamp_passed_as_string> \
  This is a required value when content_to_scrape="fresh", and it determines the point from which the scraper will start scraping backwards in time
* "data_path": Path to a local CSV file containing previously scraped Sharechat content. Currently, this is a required value when content_to_scrape="virality".  The virality scraper will scrape and update the current virality metrics for the Sharechat posts in this file. \
In future, virality metrics will be updated directly in the Sharechat Mongo DB and this key will be deprecated.
* "mode": <string_value>\
This value determines whether the scraped data should be stored only locally or locally + in a MongoDB and Amazon s3 bucket. Possible values are "local" and "archive".
* "targeting": <string_value>\
This value determines whether the scraper should scrape all tags that can be found within specified buckets, or only specified tags. The first approach is broader and well-suited for a cron job since it automates tag discovery, while the second approach offers more flexibility and precision in content curation. Possible values are "bucket" and "tag".
* "is_cron_job: <boolean_value>\
When True, the scraper manager will automatically generate the current UNIX timestamp (required by the fresh content scraper) when the cron job is triggered. This will override any UNIX timestamp that is manually entered in config.py.

*Instructions for finding your Sharechat user id, passcode, bucket ids and tag hashes:*

1. *Go to the Sharechat website homepage, sign in and select your language from the top left corner*
2. *Click on the search button at the bottom of the page. This will take you to https://sharechat.com/explore*
3. *Click on a content bucket of interest, eg. 'Sharechat Trends'*
4. *Right click on the page and click on Inspect > Network > XHR*
5. *Click on a tag of interest inside the content bucket, eg. 'Ambedkar Jayanti'. This will take you to the tag page and generate one or more of the following requests under the Name tab in the Inspect window - requestType66 / tag?tagHash... / sendPWAEvent *
6. *Look at the url in address bar. The tag hash is the alphanumeric code following https://sharechat.com/tag/*
7. *Click on the requests mentioned above and look inside the Headers and Preview tabs for each one. Your Sharechat user id and passcode, the bucket id and tag hash can be found inside these sections.*

# Immediate Roadmap

We are working on a machine learning model that will filter out any irrelevant content we scrape. We define *relevant* content as that which is misinformation, could potentially become misinformation, or is of historical value.

# Want to contribute to this repository?

We have a [guide](docs/contributing.md) for you.

