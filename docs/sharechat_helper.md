The [Sharechat helper](sharechat_helper.py) contains common helper functions for various [Sharechat scrapers](sharechat_scrapers.py). 

`generate_requests_dict(USER_ID, PASSCODE, tag_hash=None, content_type=None, unix_timestamp=None, post_key=None)`: Generates parameters for API requests. Used by all scrapers

`get_response_dict(requests_dict, request_type)`: Sends a request to the Sharechat API and returns a json response. Used by all content scrapers

`get_tag_data(payload_dict)`: Gets tag data. Returns the tag name, tag translation, tag genre, bucket name and bucket id. Used by trending, fresh and ML content scrapers

`get_common_metadata(payload_key, timestamp, language, media_type, post_permalink, caption, external_shares, likes, comments, reposts, views, profile_page)`: Gets payload metadata that is common across content types. Used by trending, fresh and ML content scrapers

`get_post_data(payload_dict, tag_name, tag_translation, tag_genre, bucket_name, bucket_id)`: Gets the tag contents i.e. the metadata for each post under the tag. Returns media_link, timestamp, language, media_type, external_shares, likes, comments, reposts, post_permalink, caption, text, views, profile_page in a dataframe. Used by trending, fresh and ML content scrapers

`get_next_offset_hash(payload_dict)`: Gets the hash that is required for scraping the next page. Used by the trending content scraper

`get_next_timestamp(payload_dict)`: Gets the timestamp that is required for scraping the next page. Used by the fresh content scraper

`get_trending_data(USER_ID, PASSCODE, tag_hashes, pages)`: Gets trending tag data. Uses the helper functions above

`get_fresh_data(USER_ID, PASSCODE, tag_hashes, pages, unix_timestamp)`: Gets fresh tag data. Uses the helper functions above

`scrape_metrics(response_dict)`: Scrapes the latest virality metrics for previously scraped content  i.e. likes, shares, comments, reposts and views. Used by virality scraper

`get_current_metrics(USER_ID, PASSCODE, post_permalink)`: Iterates through previously scraped content and updates virality metrics using scrape_metrics(). Used by virality scraper

`sharechat_s3_upload(df, aws, bucket, s3)`: Uploads scraped content to S3 bucket. Uses helper function from s3_mongo_helper.py

`sharechat_mongo_upload(df, coll)`: Uploads scraped content to MongoDB. Uses helper function from s3_mongo_helper.py

`get_thumbnails(df)`: Generates HTML file with thumbnails for image and video posts

`save_data_to_disk(df, html)`: Saves scraped data locally as CSV and HTML files