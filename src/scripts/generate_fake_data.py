#!/usr/bin/env python3
"""
Generate fake/mock data for ShopSmart Analytics development.

Generates:
- 10,000 products across 3 platforms
- 120,000+ price_history records (30 days x 4 records/day per product)
- 200,000+ reviews with diverse sentiment + fake reviews
"""

import os
import sys
import random
import math
from datetime import datetime, timedelta

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.getenv(
    'SYNC_DATABASE_URL',
    'postgresql://shopsmart:shopsmart123@localhost:5432/shopsmart_db'
)

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

# ── Vietnamese product data ─────────────────────────────────────────────────

PHONE_PRODUCTS = [
    ("iPhone 15 Pro Max 256GB", 28990000, 34990000),
    ("iPhone 15 Pro 128GB", 23990000, 28990000),
    ("iPhone 14 128GB", 17990000, 22990000),
    ("Samsung Galaxy S24 Ultra 256GB", 26990000, 31990000),
    ("Samsung Galaxy S24+ 256GB", 21990000, 25990000),
    ("Samsung Galaxy A55 5G 256GB", 8990000, 10990000),
    ("Xiaomi 14 Ultra 512GB", 22990000, 26990000),
    ("Xiaomi Redmi Note 13 Pro 256GB", 5990000, 7490000),
    ("OPPO Find X7 Ultra 512GB", 24990000, 28990000),
    ("OPPO Reno 11 5G 256GB", 7990000, 9990000),
    ("Vivo X100 Pro 256GB", 19990000, 23990000),
    ("Realme GT 5 Pro 256GB", 14990000, 17990000),
    ("OnePlus 12 256GB", 17990000, 20990000),
    ("Google Pixel 8 Pro 256GB", 22990000, 26990000),
    ("Nothing Phone 2a 256GB", 8490000, 9990000),
]

LAPTOP_PRODUCTS = [
    ("MacBook Air M3 13 inch 8GB 256GB", 28990000, 32990000),
    ("MacBook Pro M3 Pro 14 inch 18GB 512GB", 52990000, 59990000),
    ("Dell XPS 15 Core i7 16GB 512GB RTX 4060", 35990000, 42990000),
    ("HP Spectre x360 14 Core i7 16GB 1TB", 32990000, 38990000),
    ("Lenovo ThinkPad X1 Carbon Gen 12 i7 16GB 512GB", 38990000, 45990000),
    ("ASUS ROG Zephyrus G14 Ryzen 9 32GB RTX 4060", 35990000, 42990000),
    ("Acer Swift Go 14 Core Ultra 7 16GB 512GB", 18990000, 22990000),
    ("MSI Prestige 16 Core i7 16GB RTX 4060", 28990000, 34990000),
    ("Lenovo IdeaPad 5 Pro 16 Core i7 16GB 512GB", 19990000, 24990000),
    ("HP Pavilion 15 Core i5 8GB 512GB", 12990000, 15990000),
]

FASHION_PRODUCTS = [
    ("Áo thun nam Uniqlo Supima Cotton", 290000, 390000),
    ("Quần jean nữ Levi's 501 Original", 1290000, 1790000),
    ("Áo khoác nam Nike Windrunner", 1890000, 2390000),
    ("Váy đầm nữ Zara Floral Print", 890000, 1290000),
    ("Giày sneaker Nike Air Force 1", 2490000, 2990000),
    ("Giày chạy bộ Adidas Ultraboost 23", 3290000, 3990000),
    ("Túi xách nữ Coach Kat", 5990000, 7990000),
    ("Áo polo nam Lacoste Cotton Pique", 1590000, 1990000),
    ("Quần short nữ H&M Linen", 390000, 590000),
    ("Áo sơ mi nam CK Slim Fit", 990000, 1290000),
]

HOME_PRODUCTS = [
    ("Tủ lạnh Samsung Side by Side 617L", 21990000, 26990000),
    ("Máy giặt LG FV1450H3B 15kg", 14990000, 18990000),
    ("Điều hòa Daikin FTKB35WAVMV 12000BTU", 13990000, 16990000),
    ("TV Samsung Neo QLED 4K 65 inch", 32990000, 39990000),
    ("Máy lọc không khí Xiaomi Air Purifier 4 Pro", 3990000, 4990000),
    ("Nồi cơm điện Toshiba RC-18NMFVN 1.8L", 1290000, 1690000),
    ("Robot hút bụi Roomba j7+ Plus", 14990000, 18990000),
    ("Bộ nồi Happycall Diamond IH 5 món", 2490000, 3290000),
    ("Máy pha cà phê Delonghi Magnifica Start", 12990000, 16990000),
    ("Bàn làm việc Ikea LINNMON 150x75cm", 1290000, 1690000),
]

BEAUTY_PRODUCTS = [
    ("Son môi YSL Rouge Pur Couture #1", 890000, 1090000),
    ("Kem dưỡng da Estee Lauder Advanced Night Repair 50ml", 1990000, 2490000),
    ("Nước hoa Chanel Coco Mademoiselle EDP 50ml", 3290000, 3990000),
    ("Mascara Maybelline Sky High 7.2g", 189000, 259000),
    ("Kem chống nắng Anessa Perfect UV SPF50+ 60ml", 490000, 690000),
    ("Serum Vitamin C Kiehl's 30ml", 890000, 1090000),
    ("Phấn trang điểm Mac Studio Fix Powder", 790000, 990000),
    ("Dầu tẩy trang DHC Deep Cleansing Oil 200ml", 390000, 490000),
    ("Mặt nạ dưỡng ẩm Laneige Water Sleeping Mask 70ml", 490000, 690000),
    ("Serum phục hồi da Paula's Choice 2% BHA 30ml", 890000, 1190000),
]

BOOK_PRODUCTS = [
    ("Atomic Habits - Thói Quen Nguyên Tử", 79000, 99000),
    ("Đắc Nhân Tâm - Dale Carnegie", 65000, 89000),
    ("Nhà Giả Kim - Paulo Coelho", 59000, 79000),
    ("Tư Duy Nhanh Và Chậm - Daniel Kahneman", 119000, 149000),
    ("Sapiens - Lược Sử Loài Người", 139000, 169000),
    ("The Psychology of Money - Tâm Lý Tiền Bạc", 89000, 119000),
    ("Deep Work - Làm Việc Sâu", 95000, 119000),
    ("Zero to One - Peter Thiel", 79000, 99000),
    ("Bộ 3 Cuốn Kỹ Năng Giao Tiếp", 199000, 259000),
    ("Python Crash Course 3rd Edition", 299000, 379000),
]

SPORT_PRODUCTS = [
    ("Xe đạp thể thao Giant Revolt 2 2024", 12990000, 15990000),
    ("Bộ tạ tay điều chỉnh Bowflex 552 52.5lbs", 8990000, 11990000),
    ("Thảm yoga Manduka PRO 6mm", 1990000, 2490000),
    ("Giày chạy bộ Hoka Clifton 9", 3290000, 3990000),
    ("Bình nước Hydro Flask 32oz", 890000, 1190000),
    ("Dây kháng lực tập gym (bộ 5 dây)", 390000, 590000),
    ("Đồng hồ thể thao Garmin Fenix 7", 18990000, 22990000),
    ("Máy chạy bộ LifeFitness F3", 24990000, 29990000),
    ("Áo tập yoga Lululemon Align", 1890000, 2390000),
    ("Giày bóng rổ Nike LeBron 21", 4290000, 5290000),
]

FOOD_PRODUCTS = [
    ("Sữa TH True Milk Organic 1L x6", 189000, 229000),
    ("Cà phê Trung Nguyên Legend bộ 5 gói", 299000, 379000),
    ("Bột protein MyProtein Impact Whey 2.5kg", 999000, 1290000),
    ("Yến mạch Quaker Oats 4.5kg", 399000, 499000),
    ("Dầu ô liu Extra Virgin Bertolli 750ml", 289000, 359000),
    ("Mật ong nguyên chất Honeyland 500g", 199000, 249000),
    ("Hạt điều rang muối Lafooco 500g", 149000, 189000),
    ("Trà xanh Matcha Ito En 40g", 189000, 239000),
    ("Combo vitamin tổng hợp Nature Made x100", 599000, 799000),
    ("Sữa chua ăn Vinamilk mix 24 hũ", 189000, 229000),
]

ALL_PRODUCT_CATEGORIES = [
    ("dien-thoai", PHONE_PRODUCTS, "Điện thoại"),
    ("laptop", LAPTOP_PRODUCTS, "Laptop"),
    ("thoi-trang-nu", FASHION_PRODUCTS, "Thời trang"),
    ("gia-dung", HOME_PRODUCTS, "Gia dụng"),
    ("my-pham", BEAUTY_PRODUCTS, "Mỹ phẩm"),
    ("sach", BOOK_PRODUCTS, "Sách"),
    ("the-thao", SPORT_PRODUCTS, "Thể thao"),
    ("thuc-pham", FOOD_PRODUCTS, "Thực phẩm"),
]

PLATFORMS = ["tiki", "shopee", "lazada"]

SELLERS = [
    "Apple Official Store", "Samsung Official Store", "Xiaomi Official Store",
    "Nike Official Store", "Adidas Official Store", "Official Store",
    "TechShop Vietnam", "DigiWorld", "FPT Shop", "CellphoneS",
    "Thế Giới Di Động", "MediaMart", "Nguyễn Kim",
    "Shop Giá Tốt", "Hàng Chính Hãng VN", "MinhTuanMobile",
]

POSITIVE_REVIEWS = [
    "Sản phẩm rất tốt, đóng gói cẩn thận, giao hàng nhanh!",
    "Chất lượng vượt mong đợi, giá hợp lý, sẽ mua lại.",
    "Hàng chính hãng, đúng mô tả. Shop uy tín!",
    "Rất hài lòng với sản phẩm này. Recommend cho mọi người!",
    "Giao hàng siêu nhanh, sản phẩm y hình. 5 sao!",
    "Mua lần 2 rồi vẫn thấy ổn, chất lượng tốt.",
    "Shop phản hồi nhanh, sản phẩm đúng như mô tả.",
    "Hài lòng lắm, sản phẩm bền đẹp xài cũng được.",
    "Giá tốt, chất lượng không thua kém hàng đắt hơn.",
    "Mua về dùng thấy ổn, đúng như quảng cáo.",
]

NEUTRAL_REVIEWS = [
    "Sản phẩm tạm ổn, không có gì đặc biệt.",
    "Bình thường, không tệ nhưng cũng không xuất sắc.",
    "Hàng nhận được đúng như mô tả, không hơn không kém.",
    "Chất lượng như tầm giá, cũng được.",
    "Giao hàng hơi chậm nhưng sản phẩm ổn.",
]

NEGATIVE_REVIEWS = [
    "Hàng không đúng như mô tả, thất vọng!",
    "Chất lượng kém hơn mong đợi, không đáng tiền.",
    "Giao hàng chậm, đóng gói không cẩn thận.",
    "Sản phẩm lỗi ngay từ đầu, phải đổi trả.",
    "Shop không support tốt khi có vấn đề.",
]

FAKE_REVIEWS = [
    "Tốt lắm! Mua ngay đi mọi người!",
    "5 sao 5 sao 5 sao! Tuyệt vời!",
    "Mua đi không hối hận đâu!",
    "Hàng đẹp lắm mua đi mọi người ơi!",
    "Sản phẩm tốt, shop uy tín, giao nhanh, đóng gói đẹp!",
]

# ── Price pattern generators ────────────────────────────────────────────────

def generate_price_pattern(base_price: int, days: int = 30, pattern: str = "stable") -> list:
    """Generate price history with different patterns."""
    prices = []

    if pattern == "decreasing":
        # Gradually decreasing (sale incoming)
        for i in range(days * 4):
            factor = 1.0 - (i / (days * 4)) * 0.15
            noise = np.random.normal(0, 0.01)
            price = int(base_price * (factor + noise))
            prices.append(max(price, int(base_price * 0.8)))

    elif pattern == "increasing":
        # Gradually increasing (popular item)
        for i in range(days * 4):
            factor = 1.0 + (i / (days * 4)) * 0.10
            noise = np.random.normal(0, 0.01)
            price = int(base_price * (factor + noise))
            prices.append(price)

    elif pattern == "flash_sale":
        # Normal → sudden drop → back to normal
        spike_start = days * 4 // 3
        spike_end = spike_start + 8  # 2 days of sale
        for i in range(days * 4):
            if spike_start <= i <= spike_end:
                factor = 0.70 + np.random.normal(0, 0.02)  # 30% off
            else:
                factor = 1.0 + np.random.normal(0, 0.01)
            price = int(base_price * factor)
            prices.append(max(price, int(base_price * 0.5)))

    elif pattern == "volatile":
        # High volatility
        for i in range(days * 4):
            factor = 1.0 + np.random.normal(0, 0.05)
            price = int(base_price * factor)
            prices.append(max(price, int(base_price * 0.7)))

    else:  # stable
        for i in range(days * 4):
            noise = np.random.normal(0, 0.008)
            price = int(base_price * (1.0 + noise))
            prices.append(price)

    return prices


# ── Main generation ──────────────────────────────────────────────────────────

def get_platform_ids(session) -> dict:
    result = session.execute(text("SELECT id, name FROM platforms"))
    return {row[1]: row[0] for row in result}


def get_category_ids(session) -> dict:
    result = session.execute(text("SELECT id, slug FROM categories"))
    return {row[1]: row[0] for row in result}


def generate_products(session, platform_ids: dict, category_ids: dict) -> list:
    """Generate 10,000 products and return their IDs + base prices."""
    print(f"\n🛍️  Generating products...")

    product_ids = []
    total = 0
    target = 10000

    # How many variants per product template
    products_per_template = target // (len(ALL_PRODUCT_CATEGORIES) * 15) + 1

    while total < target:
        for cat_slug, product_list, cat_name in ALL_PRODUCT_CATEGORIES:
            if total >= target:
                break

            category_id = category_ids.get(cat_slug)

            for base_name, base_price, base_original in product_list:
                if total >= target:
                    break

                for variant in range(products_per_template):
                    if total >= target:
                        break

                    platform = random.choice(PLATFORMS)
                    platform_id = platform_ids.get(platform)
                    if not platform_id:
                        continue

                    # Price variation ±15%
                    price_factor = random.uniform(0.85, 1.15)
                    current_price = int(base_price * price_factor)
                    original_price = int(base_original * price_factor)

                    if original_price <= current_price:
                        original_price = int(current_price * random.uniform(1.1, 1.4))

                    discount = round((original_price - current_price) / original_price * 100, 2)

                    external_id = f"{platform[:3].upper()}{cat_slug[:3].upper()}{total:06d}"
                    name_variant = f"{base_name}" if variant == 0 else f"{base_name} - Phiên bản {variant + 1}"

                    seller = random.choice(SELLERS)
                    rating_avg = round(random.uniform(3.5, 5.0), 1)
                    rating_count = random.randint(10, 5000)
                    total_sold = random.randint(50, 50000)

                    url = f"https://{platform}.vn/{cat_slug}/{external_id.lower()}"
                    image_url = f"https://cdn.{platform}.vn/products/{external_id.lower()}.jpg"

                    now = datetime.utcnow()
                    first_seen = now - timedelta(days=random.randint(30, 365))
                    last_crawled = now - timedelta(hours=random.randint(0, 6))

                    try:
                        result = session.execute(text("""
                            INSERT INTO products (
                                platform_id, category_id, external_id, name, url, image_url,
                                seller_name, current_price, original_price, discount_percent,
                                rating_avg, rating_count, total_sold, is_official_store,
                                is_active, first_seen_at, last_crawled_at, created_at, updated_at
                            ) VALUES (
                                :platform_id, :category_id, :external_id, :name, :url, :image_url,
                                :seller_name, :current_price, :original_price, :discount_percent,
                                :rating_avg, :rating_count, :total_sold, :is_official,
                                TRUE, :first_seen, :last_crawled, :now, :now
                            )
                            ON CONFLICT (platform_id, external_id) DO UPDATE SET
                                current_price = EXCLUDED.current_price,
                                updated_at = EXCLUDED.updated_at
                            RETURNING id
                        """), {
                            "platform_id": platform_id,
                            "category_id": category_id,
                            "external_id": external_id,
                            "name": name_variant[:500],
                            "url": url,
                            "image_url": image_url,
                            "seller_name": seller,
                            "current_price": current_price,
                            "original_price": original_price,
                            "discount_percent": discount,
                            "rating_avg": rating_avg,
                            "rating_count": rating_count,
                            "total_sold": total_sold,
                            "is_official": seller.endswith("Official Store"),
                            "first_seen": first_seen,
                            "last_crawled": last_crawled,
                            "now": now,
                        })

                        product_id = result.fetchone()[0]
                        product_ids.append((product_id, current_price, base_price))
                        total += 1

                        if total % 1000 == 0:
                            session.commit()
                            print(f"  {total:,} products created...")

                    except Exception as e:
                        session.rollback()
                        continue

    session.commit()
    print(f"  ✅ Created {total:,} products")
    return product_ids


def generate_price_history(session, product_data: list):
    """Generate 30 days of price history (4 records/day per product)."""
    print(f"\n📈 Generating price history...")

    patterns = ["stable", "stable", "stable", "decreasing", "increasing", "flash_sale", "volatile"]

    batch = []
    total = 0
    BATCH_SIZE = 5000

    for product_id, current_price, base_price in product_data:
        pattern = random.choice(patterns)
        prices = generate_price_pattern(base_price, days=30, pattern=pattern)

        now = datetime.utcnow()

        for i, price in enumerate(prices):
            # 4 records per day = one every 6 hours
            hours_ago = (len(prices) - i) * 6
            crawled_at = now - timedelta(hours=hours_ago)

            original = int(price * random.uniform(1.1, 1.4))
            discount = round((original - price) / original * 100, 2)

            batch.append({
                "product_id": product_id,
                "price": price,
                "original_price": original,
                "discount_percent": discount,
                "in_stock": random.random() > 0.05,  # 95% in stock
                "crawled_at": crawled_at,
                "created_at": crawled_at,
            })

            total += 1

        if len(batch) >= BATCH_SIZE:
            session.execute(text("""
                INSERT INTO price_history (product_id, price, original_price, discount_percent, in_stock, crawled_at, created_at)
                VALUES (:product_id, :price, :original_price, :discount_percent, :in_stock, :crawled_at, :created_at)
            """), batch)
            session.commit()
            batch = []
            print(f"  {total:,} price records inserted...")

    if batch:
        session.execute(text("""
            INSERT INTO price_history (product_id, price, original_price, discount_percent, in_stock, crawled_at, created_at)
            VALUES (:product_id, :price, :original_price, :discount_percent, :in_stock, :crawled_at, :created_at)
        """), batch)
        session.commit()

    print(f"  ✅ Created {total:,} price history records")


def generate_reviews(session, product_data: list):
    """Generate reviews with diverse sentiment including fake reviews."""
    print(f"\n💬 Generating reviews...")

    total = 0
    BATCH_SIZE = 2000
    batch = []

    for product_id, current_price, base_price in product_data:
        # 10-30 reviews per product
        num_reviews = random.randint(10, 30)
        fake_ratio = random.uniform(0.0, 0.20)  # 0-20% fake

        for i in range(num_reviews):
            is_fake = random.random() < fake_ratio

            if is_fake:
                content = random.choice(FAKE_REVIEWS)
                rating = 5
                sentiment_score = round(random.uniform(0.8, 1.0), 3)
            else:
                # Natural distribution
                rand = random.random()
                if rand < 0.65:   # 65% positive
                    content = random.choice(POSITIVE_REVIEWS)
                    rating = random.choices([4, 5], weights=[30, 70])[0]
                    sentiment_score = round(random.uniform(0.3, 1.0), 3)
                elif rand < 0.85: # 20% neutral
                    content = random.choice(NEUTRAL_REVIEWS)
                    rating = random.choices([3, 4], weights=[60, 40])[0]
                    sentiment_score = round(random.uniform(-0.1, 0.3), 3)
                else:             # 15% negative
                    content = random.choice(NEGATIVE_REVIEWS)
                    rating = random.choices([1, 2, 3], weights=[30, 40, 30])[0]
                    sentiment_score = round(random.uniform(-1.0, -0.1), 3)

            days_ago = random.randint(1, 90)
            created_date = datetime.utcnow() - timedelta(days=days_ago)

            external_id = f"REV{product_id:06d}{i:04d}"
            author = f"User{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}"

            batch.append({
                "product_id": product_id,
                "external_id": external_id,
                "author_name": author,
                "rating": rating,
                "content": content,
                "created_date": created_date,
                "likes_count": random.randint(0, 50),
                "is_purchased": random.random() > 0.3,
                "sentiment_score": sentiment_score,
                "is_fake": is_fake,
                "fake_confidence": round(random.uniform(0.75, 0.99), 3) if is_fake else round(random.uniform(0.0, 0.2), 3),
                "crawled_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
            })

            total += 1

        if len(batch) >= BATCH_SIZE:
            session.execute(text("""
                INSERT INTO reviews (
                    product_id, external_id, author_name, rating, content,
                    created_date, likes_count, is_purchased, sentiment_score,
                    is_fake, fake_confidence, crawled_at, created_at
                ) VALUES (
                    :product_id, :external_id, :author_name, :rating, :content,
                    :created_date, :likes_count, :is_purchased, :sentiment_score,
                    :is_fake, :fake_confidence, :crawled_at, :created_at
                )
                ON CONFLICT (product_id, external_id) DO NOTHING
            """), batch)
            session.commit()
            batch = []
            print(f"  {total:,} reviews inserted...")

    if batch:
        session.execute(text("""
            INSERT INTO reviews (
                product_id, external_id, author_name, rating, content,
                created_date, likes_count, is_purchased, sentiment_score,
                is_fake, fake_confidence, crawled_at, created_at
            ) VALUES (
                :product_id, :external_id, :author_name, :rating, :content,
                :created_date, :likes_count, :is_purchased, :sentiment_score,
                :is_fake, :fake_confidence, :crawled_at, :created_at
            )
            ON CONFLICT (product_id, external_id) DO NOTHING
        """), batch)
        session.commit()

    print(f"  ✅ Created {total:,} reviews")


def generate_analytics(session, product_data: list):
    """Generate product_analytics records for today."""
    print(f"\n📊 Generating analytics...")

    batch = []
    total = 0
    BATCH_SIZE = 1000
    today = datetime.utcnow().date()

    buy_signals = ["strong_buy", "buy", "hold", "wait"]
    signal_weights = [10, 25, 40, 25]
    trends = ["up", "down", "stable"]
    trend_weights = [25, 35, 40]

    for product_id, current_price, base_price in product_data:
        min_p = int(current_price * random.uniform(0.85, 0.98))
        max_p = int(current_price * random.uniform(1.02, 1.20))
        avg_p = int((min_p + max_p) / 2)

        volatility = round(random.uniform(0.01, 0.08), 4)
        trend = random.choices(trends, weights=trend_weights)[0]
        signal = random.choices(buy_signals, weights=signal_weights)[0]
        anomaly = round(random.uniform(0.0, 0.4), 3)

        predicted = int(current_price * (0.95 if trend == "down" else 1.05 if trend == "up" else 1.0))

        batch.append({
            "product_id": product_id,
            "date": today,
            "min_price": min_p,
            "max_price": max_p,
            "avg_price": avg_p,
            "price_volatility": volatility,
            "trend_direction": trend,
            "predicted_price_7d": predicted,
            "anomaly_score": anomaly,
            "buy_signal": signal,
            "created_at": datetime.utcnow(),
        })
        total += 1

        if len(batch) >= BATCH_SIZE:
            session.execute(text("""
                INSERT INTO product_analytics (
                    product_id, date, min_price, max_price, avg_price,
                    price_volatility, trend_direction, predicted_price_7d,
                    anomaly_score, buy_signal, created_at
                ) VALUES (
                    :product_id, :date, :min_price, :max_price, :avg_price,
                    :price_volatility, :trend_direction, :predicted_price_7d,
                    :anomaly_score, :buy_signal, :created_at
                )
                ON CONFLICT (product_id, date) DO NOTHING
            """), batch)
            session.commit()
            batch = []

    if batch:
        session.execute(text("""
            INSERT INTO product_analytics (
                product_id, date, min_price, max_price, avg_price,
                price_volatility, trend_direction, predicted_price_7d,
                anomaly_score, buy_signal, created_at
            ) VALUES (
                :product_id, :date, :min_price, :max_price, :avg_price,
                :price_volatility, :trend_direction, :predicted_price_7d,
                :anomaly_score, :buy_signal, :created_at
            )
            ON CONFLICT (product_id, date) DO NOTHING
        """), batch)
        session.commit()

    print(f"  ✅ Created {total:,} analytics records")


def main():
    print("🚀 ShopSmart Analytics — Mock Data Generator")
    print("=" * 50)

    with Session() as session:
        # Load reference data
        platform_ids = get_platform_ids(session)
        category_ids = get_category_ids(session)

        print(f"Platforms: {list(platform_ids.keys())}")
        print(f"Categories: {len(category_ids)} loaded")

        if not platform_ids:
            print("❌ No platforms found! Run seed_data.py first.")
            sys.exit(1)

        # Generate data
        product_data = generate_products(session, platform_ids, category_ids)
        generate_price_history(session, product_data)
        generate_reviews(session, product_data)
        generate_analytics(session, product_data)

    print("\n" + "=" * 50)
    print("✅ Mock data generation complete!")
    print(f"   Products:      ~{len(product_data):,}")
    print(f"   Price history: ~{len(product_data) * 120:,}")
    print(f"   Reviews:       ~{len(product_data) * 20:,}")
    print(f"   Analytics:     ~{len(product_data):,}")


if __name__ == '__main__':
    main()
