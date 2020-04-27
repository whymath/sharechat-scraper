Scraper function loaded from sharechat_scrapers.py. Runs when content_to_scrape="virality" in config.py. Scrapes the current virality metrics for previously scraped Sharechat content. Works best when the content has been very recently scraped by the fresh content scraper, as virality tracking is found to be most insightful early in the life cycle of social media posts. 

The virality scraper's objective is to help understand the growth cycle for posts on Sharechat and similar platforms in terms of virality metrics like views, likes, shares, comments and reposts. It can be run daily on batches of fresh content to track how posts grow, peak and plateau. It is currently in the local development stage.

### Scraper workflow:

The scraper performs the following steps using helper functions imported from sharechat_helper.py 

1. Loads a CSV file containing post data scraped by one of Tattle's Sharechat content scrapers. Ideally this is recent data scraped by the fresh content scraper. The data is stored in a dataframe called df
2. Calculates the difference (number of days) between the present day and 't', the day on which the data was posted. For this to work properly, all timestamps in the "timestamp" column of the loaded data must be from the same day
3. Initializes an empty dataframe called results_df to hold the scraped metrics. The column names are suffixed with t+'n', where 'n' is the difference calculated in step 2
4. Starts a loop that does the following for each row (post) in the dataframe:
   * Extracts the post key from the post_permalink
   * Generates a request dictionary with a helper function called generate_requests_dict()
   * Sends a requestType45 using the helper function get_response_dict(). This returns a json response containing the latest data about the post
   * Scrapes the json response with the helper function get_virality_metrics(). The result is appended to the results_df dataframe
   * Updates the progress bar 
5.  Concatenates df and results_df, so that the virality metrics for t+'n' (i.e the present day) are added to each post (row)
6. Saves the updated data locally (development stage only)
7. Repeats the process on days t + ...

