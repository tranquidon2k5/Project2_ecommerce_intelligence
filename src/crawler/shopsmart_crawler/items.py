import scrapy


class ProductItem(scrapy.Item):
    # Product info
    name = scrapy.Field()
    price = scrapy.Field()               # Current price (VND integer)
    original_price = scrapy.Field()      # Original price before discount
    url = scrapy.Field()
    image_url = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    sold_count = scrapy.Field()
    seller_name = scrapy.Field()
    seller_rating = scrapy.Field()
    is_official_store = scrapy.Field()

    # Platform/classification
    platform = scrapy.Field()            # 'shopee', 'tiki', 'lazada'
    external_id = scrapy.Field()         # Platform's product ID
    category = scrapy.Field()            # Category name/slug
    category_id = scrapy.Field()         # Tiki category ID

    # Computed
    discount_percent = scrapy.Field()


class ReviewItem(scrapy.Item):
    product_external_id = scrapy.Field()
    platform = scrapy.Field()
    external_id = scrapy.Field()
    author_name = scrapy.Field()
    rating = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    likes_count = scrapy.Field()
    is_purchased = scrapy.Field()
