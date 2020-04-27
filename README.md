# Introduction

This repository contains code for scraping publicly available data from targeted content tags on the Indian social network https://sharechat.com/

![Sharechat Content Tree]sharechat_content_tree.png

# Why are we scraping this data?

One of Tattle's key goals is to create new knowledge around misinformation/disinformation on social media in India. To this end, we're creating an open archive of relevant multilingual content circulated on chat apps and social networks such as Sharechat. Learn more about our goals and values here - https://tattle.co.in/faq

# Running locally

1. Create an account on Sharechat
2. Fork the repository 
3. Install required Python packages: `pip install requirements.txt`
4. Set up an AWS S3 bucket to store the scraped content (images, videos, text) and a MongoDB to store the scraped metadata (timestamps, likes, shares etc.)\
If you can't set up a MongoDB or S3 bucket, simply comment out the lines which initialize and upload data to S3 and MongoDB in the relevant scraper script. Scraper scripts can be found in sharechat_scrapers.py. If you need help doing this, please reach out to us. 
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
6. Modify the Config file as per your requirements, then run it to start scraping.

## Modifying the Config file

config.py is the only script you need to run to start scraping. It contains a dictionary named scraper_params. Depending on the values entered in this dictionary, the manager.py called by config.py will run one of the following Sharechat scrapers - 

docs/Sharechat trending content scraper.md

docs/Sharechat fresh content scraper.md

docs/Sharechat ML scraper.md

docs/Sharechat virality scraper.md (development stage)

**Usage**: Enter values in the scraper_params dictionary as per the scraping requirement, then run the file.

scraper_params takes the following key:value pairs -

* "USER_ID": os.environ.get("SHARECHAT_USER_ID") 
* "PASSCODE": os.environ.get("SHARECHAT_PASSCODE")
  These two key:value pairs are required by all the scrapers in order to send requests to the Sharechat API. Your user id and passcode may unfortunately not be very obvious, but instructions for finding them are given below. 
* tag_hashes: <tag_hashes_passed_as_list_of_strings>\
  Tag hashes are identifiers for content tags. These must be selected after a manual inspection of tags on Sharechat. Instructions for finding tag hashes are given below. 
*  content_to_scrape: <string>\
  This value determines which scraper will be launched by the scraper manager. Possible values are "trending", "fresh", "ml" and "virality"
*  pages: <integer>\
  Number of pages to scrape. One page typically contains 10 posts. This is a required value when content_to_scrape = "trending" or "fresh" or "ml". This number should be kept reasonably low to avoid bombarding the Sharechat API with requests.
* unix_timestamp: <10_digit_unix_timestamp_passed_as_string> \
  This is a required value when content_to_scrape="fresh", and it determines the point from which the scraper will start scraping backwards in time
* data_path: Path to a local CSV file containing previously scraped Sharechat content. Currently, this is a required value when content_to_scrape="virality".  The virality scraper will scrape and update the current virality metrics for the Sharechat posts in this file. \
In future, virality metrics will be updated directly in the Sharechat Mongo DB and this key will be removed from scraper_params.

*Instructions for finding your Sharechat user id, passcode and tag hashes:*

1. *Go to the Sharechat website homepage, sign in and select your language from the top left corner*
2. *Click on the search button at the bottom of the page. This will take you to https://sharechat.com/explore
3. *Click on a content bucket of interest, eg. 'Sharechat Trends'*
4. *Right click on the page and click on Inspect > Network > XHR*
5. *Click on a tag of interest inside the content bucket, eg. 'Ambedkar Jayanti'. This will generate a requestType66 under the Name tab in the Inspect window and take you to the tag page*
6. *Look at the url in address bar. The tag hash is the alphanumeric code following (https://sharechat.com/tag/
7. *Click on requestType66 *
   * *Click on Headers > Request Payload. Your Sharechat user id and passcode can be seen inside the request payload. (They can also be seen inside the request payloads for other types of requests*
   * *Click on Preview > payload. The tag hash will also be found inside this response payload, so you can confirm that it matches the tag hash in the url*

# Immediate Roadmap

We are working on a machine learning model that will filter out any irrelevant content we scrape. We define *relevant *content as that which is misinformation, could potentially become misinformation, or is of historical value.

# Contributing

Firstly, we are really grateful that you are considering contributing to Tattle. We welcome contributions of all sorts - filing a bug report, suggesting improvements, proposing new feature, adding documentations, writing tests etc. 

By contributing to Tattle, you are agreeing to our community guidelines (will be linked soon)

Contributing to Tattle takes 4 easy steps

1. 👋Say Hi
2. 🔨Do your thing
3. 📞Tell us 
4. 🎉Celebrate

## 👋Say Hi

The very first thing you should do is letting us know that you are interested in contributing by the following means : 

1. If you are unsure about how to contribute, simply join our Slack and introduce yourself and mention what interests you about us. We'll reach out and assist you further.
2. If there's a particular improvement you want to suggest, or a bug you want to fix, simply create a Github Issue regarding it and we'll reach out to assist you further.

## 🔨Do your thing

The Running Locally section above should help you access and run the code. Once you are able to run the code locally, you can make the changes you want. Test the features and add appropriate documentation for it if needed.

### Pair programming

We offer pair programming sessions with community members to familiarize them with the product and the code base. This will give you an opportunity to clarify any doubts regarding the codebase and the features that interest you.

## 📞Tell us 

All code changes happen via pull request. We use [Github Flow](https://guides.github.com/introduction/flow/). The easiest way to let us know if you want to combine your changes into the core code is to make a Pull Request (PR)

In your PR, please mention the following :

* What does this PR do?
* How do we test this PR?

We don't strictly follow test driven development (TDD) but any contributions that include tests are greatly appreciated.

## 🎉Celebrate

We typically review a PR within 2-3 days. We might offer you some feedback to your PR and merge it! If you reached till this stage, Congratulations and join us afterwards for virtual coffee and tea on slack 🙂

# Licence

When you submit code changes, your submissions are understood to be under the same licence that covers the project - GPL . Feel free to contact the maintainers if that's a concern.

# 