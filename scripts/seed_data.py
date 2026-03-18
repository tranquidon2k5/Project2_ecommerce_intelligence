#!/usr/bin/env python3
"""Seed initial data: platforms and categories."""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.getenv(
    'SYNC_DATABASE_URL',
    'postgresql://shopsmart:shopsmart123@localhost:5432/shopsmart_db'
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def seed_platforms(session):
    """Insert 3 Vietnamese e-commerce platforms."""
    platforms = [
        {'name': 'shopee', 'base_url': 'https://shopee.vn', 'is_active': True},
        {'name': 'tiki', 'base_url': 'https://tiki.vn', 'is_active': True},
        {'name': 'lazada', 'base_url': 'https://lazada.vn', 'is_active': True},
    ]

    for p in platforms:
        existing = session.execute(
            text("SELECT id FROM platforms WHERE name = :name"),
            {'name': p['name']}
        ).fetchone()

        if not existing:
            session.execute(
                text("""
                    INSERT INTO platforms (name, base_url, is_active, created_at)
                    VALUES (:name, :base_url, :is_active, :created_at)
                """),
                {**p, 'created_at': datetime.utcnow()}
            )
            print(f"  ✓ Platform: {p['name']}")
        else:
            print(f"  - Platform already exists: {p['name']}")

    session.commit()


def seed_categories(session):
    """Insert ~20 categories with parent-child hierarchy."""
    # Parent categories (no parent_id)
    parent_categories = [
        {'name': 'Điện thoại & Phụ kiện', 'slug': 'dien-thoai-phu-kien'},
        {'name': 'Máy tính & Laptop', 'slug': 'may-tinh-laptop'},
        {'name': 'Thời trang', 'slug': 'thoi-trang'},
        {'name': 'Gia dụng & Nội thất', 'slug': 'gia-dung-noi-that'},
        {'name': 'Mỹ phẩm & Sắc đẹp', 'slug': 'my-pham-sac-dep'},
        {'name': 'Sách & Văn phòng phẩm', 'slug': 'sach-van-phong-pham'},
        {'name': 'Thể thao & Du lịch', 'slug': 'the-thao-du-lich'},
        {'name': 'Thực phẩm & Đồ uống', 'slug': 'thuc-pham-do-uong'},
    ]

    parent_ids = {}

    for cat in parent_categories:
        existing = session.execute(
            text("SELECT id FROM categories WHERE slug = :slug"),
            {'slug': cat['slug']}
        ).fetchone()

        if not existing:
            result = session.execute(
                text("""
                    INSERT INTO categories (name, slug, parent_id, created_at)
                    VALUES (:name, :slug, NULL, :created_at)
                    RETURNING id
                """),
                {**cat, 'created_at': datetime.utcnow()}
            )
            cat_id = result.fetchone()[0]
            parent_ids[cat['slug']] = cat_id
            print(f"  ✓ Category: {cat['name']}")
        else:
            parent_ids[cat['slug']] = existing[0]
            print(f"  - Category already exists: {cat['name']}")

    session.commit()

    # Child categories
    child_categories = [
        {'name': 'Điện thoại', 'slug': 'dien-thoai', 'parent_slug': 'dien-thoai-phu-kien'},
        {'name': 'Tai nghe', 'slug': 'tai-nghe', 'parent_slug': 'dien-thoai-phu-kien'},
        {'name': 'Ốp lưng & Phụ kiện', 'slug': 'op-lung-phu-kien', 'parent_slug': 'dien-thoai-phu-kien'},
        {'name': 'Laptop', 'slug': 'laptop', 'parent_slug': 'may-tinh-laptop'},
        {'name': 'Máy tính bàn', 'slug': 'may-tinh-ban', 'parent_slug': 'may-tinh-laptop'},
        {'name': 'Phụ kiện máy tính', 'slug': 'phu-kien-may-tinh', 'parent_slug': 'may-tinh-laptop'},
        {'name': 'Thời trang nam', 'slug': 'thoi-trang-nam', 'parent_slug': 'thoi-trang'},
        {'name': 'Thời trang nữ', 'slug': 'thoi-trang-nu', 'parent_slug': 'thoi-trang'},
        {'name': 'Giày dép', 'slug': 'giay-dep', 'parent_slug': 'thoi-trang'},
        {'name': 'Đồ gia dụng', 'slug': 'do-gia-dung', 'parent_slug': 'gia-dung-noi-that'},
        {'name': 'Nội thất', 'slug': 'noi-that', 'parent_slug': 'gia-dung-noi-that'},
        {'name': 'Chăm sóc da', 'slug': 'cham-soc-da', 'parent_slug': 'my-pham-sac-dep'},
        {'name': 'Trang điểm', 'slug': 'trang-diem', 'parent_slug': 'my-pham-sac-dep'},
    ]

    for cat in child_categories:
        parent_slug = cat.pop('parent_slug')
        parent_id = parent_ids.get(parent_slug)

        existing = session.execute(
            text("SELECT id FROM categories WHERE slug = :slug"),
            {'slug': cat['slug']}
        ).fetchone()

        if not existing:
            session.execute(
                text("""
                    INSERT INTO categories (name, slug, parent_id, created_at)
                    VALUES (:name, :slug, :parent_id, :created_at)
                """),
                {**cat, 'parent_id': parent_id, 'created_at': datetime.utcnow()}
            )
            print(f"    ✓ Sub-category: {cat['name']}")
        else:
            print(f"    - Sub-category already exists: {cat['name']}")

    session.commit()


def main():
    print("🌱 Seeding database...")
    print("\n📦 Platforms:")

    with Session() as session:
        seed_platforms(session)
        print("\n📁 Categories:")
        seed_categories(session)

    print("\n✅ Seed complete!")


if __name__ == '__main__':
    main()
