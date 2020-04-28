Scraper function loaded from [Sharechat scrapers](../sharechat_scrapers.py). Runs when content_to_scrape="ml" in [Config](../config.py). Scrapes content from the "trending" tab on the tag page. The scraped content will not be chronological.

The ML scraper's workflow is identical to the trending content scraper, except that the scraped content is saved in different S3 and Mongo DB locations. Its purpose is to scrape training data samples for a machine learning model that will filter out "irrelevant" content we scrape in the future. This will help us make Tattle's content archive more relevant and useful for fact-checkers and researchers. 

We have targeted a variety of tags with this scraper, whose names / English translations are given below -

good night, good morning, mohabbat dil se, dard e dil, blessings, \
life lessons, time pass, funny images, bollywood gossip, cricket info,\
lord vishnu, facebook jokes, whatsapp status, romantic photos,\
love shayari status, good evening, jai shree krishna, shree ganesh,\
mahadev's arrival, ram laxman, good thoughts, motivational quotes,\
satyavachan, jokes, husband wife jokes, friendship jokes, comedy video,\
girl boy jokes, single jokes, kapil sharma fun videos, election jokes,\
funny videos, aur batao, girls nautanki, dubsmash, birthday, \
good wishes videos, my life, my love, betrayal, sunset, nature photography,\
beautiful waterfalls, nature love, wallpaper, dance, bikes and cars,\
sports bikes, family quotes