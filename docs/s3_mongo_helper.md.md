The [S3 Mongo helper](s3_mongo_helper.py) contains helper functions to upload data to MongoDB and S3. These can be adapted for various scrapers.

`initialize_s3()`: Initializes Boto S3 connection. Requires S3 credentials to be stored in .env file

`initialize_mongo()`: Initializes Pymongo MongoDB connection. Requires Mongo credentials to be stored in .env file

`upload_to_s3(s3, file, filename, bucket, content_type)`: Uploads a file to S3 via Boto client

`upload_to_mongo(data, coll)`: Uploads a file to Mongo 

`count_s3_files(s3, bucket)`: Paginates through the S3 bucket and returns the total number of files

f`ilter_s3_files(s3, bucket, start_date, end_date)`: Filters and returns S3 files that were uploaded/modified in particular a date range

`delete_s3_files(s3, bucket, start_date, end_date)`: Deletes S3 files that were uploaded/modified in particular a date range