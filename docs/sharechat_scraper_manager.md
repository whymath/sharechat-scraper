The [Sharechat Manager](../manager.py) is called when a user runs [Config](../config.py). Depending on the values the user enters in config, the manager will run one of the following scrapers from [Sharechat scrapers](../sharechat_scrapers.py) -

1. Trending content scraper - Scrapes content from the "trending" tab on the tag page, which is also the default landing page of the tag. The scraped content will not be chronological.
Read the scraper workflow [here](sharechat_trending_content_scraper.md)

2. Fresh content scraper - Scrapes content from the "fresh" tab on the tag page. It allows the user to get content posted around / leading up to a particular date and time, which is determined by the "unix_timestamp" value in config. The scraped content will be chronological.
Read the scraper workflow [here](sharechat_fresh_content_scraper.md)   

3. ML scraper - Identical to trending content scraper except that the scraped content is saved in different locations. We use this to scrape training data samples for a machine learning model that will make Tattle's content archive more useful for fact-checkers and researchers.
Read more about it [here](sharechat_ml_scraper.md) 

4. Virality scraper - Scrapes the current virality metrics for previously scraped Sharechat content. Works best when the content has been very recently scraped by the fresh content scraper, as virality tracking is found to be most insightful early in the life cycle of social media posts. 
Read the scraper workflow [here](sharechat_virality_scraper.md) (development stage)