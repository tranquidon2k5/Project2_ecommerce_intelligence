BOT_NAME = "shopsmart_crawler"

SPIDER_MODULES = ["shopsmart_crawler.spiders"]
NEWSPIDER_MODULE = "shopsmart_crawler.spiders"

# Anti-bot settings
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 4

# User agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Pipelines
ITEM_PIPELINES = {
    "shopsmart_crawler.pipelines.CleaningPipeline": 100,
    "shopsmart_crawler.pipelines.PostgresPipeline": 200,
}

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    "shopsmart_crawler.middlewares.RandomUserAgentMiddleware": 400,
}

# Logging
LOG_LEVEL = "INFO"

# Retry
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 429]

# Circuit breaker: stop if >20% errors
CLOSESPIDER_ERRORCOUNT = 50

# Feed export
FEEDS = {}
