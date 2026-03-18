# 🛒 E-Commerce Intelligence Platform
## ShopSmart Analytics

---

## 1. Mô tả dự án

**ShopSmart Analytics** là nền tảng theo dõi và phân tích giá sản phẩm trên các sàn thương mại điện tử Việt Nam (Shopee, Tiki, Lazada). Hệ thống thu thập dữ liệu hàng loạt, phân tích xu hướng giá, phát hiện đánh giá giả, và đưa ra gợi ý mua sắm thông minh cho người dùng.

## 2. Mục tiêu

### Business Goals
- Giúp người dùng mua hàng đúng thời điểm, tiết kiệm tiền
- Phát hiện sản phẩm có đánh giá giả / giá ảo
- Cung cấp cái nhìn toàn cảnh về xu hướng giá thị trường

### Technical Goals (Ghi vào CV)
- **Big Data**: Thu thập & xử lý 10,000+ sản phẩm, pipeline ETL tự động
- **AI/ML**: Price prediction, anomaly detection, fake review detection, recommendation
- **Web**: Dashboard real-time, responsive, UX chuyên nghiệp

## 3. Scope (2-4 tuần, 1 người)

### ✅ MVP - Phải có (Sprint 1-2)
- Crawl dữ liệu sản phẩm từ ít nhất 1 sàn TMĐT
- Lưu trữ lịch sử giá theo thời gian
- Dashboard hiển thị biến động giá, so sánh sản phẩm
- API RESTful hoàn chỉnh
- Search & filter sản phẩm

### ✅ AI Features (Sprint 3)
- Dự đoán xu hướng giá (lên/xuống) trong 7 ngày tới
- Phát hiện anomaly (giá bất thường, flash sale giả)
- Fake review detection (NLP sentiment analysis)
- Recommend thời điểm mua tốt nhất

### ✅ Polish (Sprint 4)
- Price alert (thông báo khi giá giảm)
- So sánh giá cross-platform
- Export báo cáo
- Deploy lên cloud

### ❌ Ngoài scope
- Mobile app
- Payment integration
- User authentication phức tạp (chỉ cần basic)

## 4. Tech Stack

| Layer | Technology | Lý do chọn |
|-------|-----------|-------------|
| **Frontend** | React 18 + TailwindCSS | Đã quen, ecosystem lớn |
| **Backend** | FastAPI (Python) | Async, nhanh, auto docs |
| **Database** | PostgreSQL | Relational, time-series queries tốt |
| **Cache** | Redis | Cache kết quả crawl, rate limiting |
| **Crawler** | Scrapy + Playwright | Scrapy cho tốc độ, Playwright cho JS-rendered pages |
| **AI/ML** | scikit-learn, Prophet, transformers | Prediction, anomaly, NLP |
| **Big Data** | Apache Airflow | Orchestrate ETL pipeline |
| **Containerization** | Docker Compose | Đã quen, dễ deploy |
| **Monitoring** | Grafana + Prometheus | Dashboard monitoring pipeline |

## 5. Điểm nhấn CV

Khi viết vào CV, project này cho phép bạn highlight:

```
E-Commerce Intelligence Platform | Python, React, PostgreSQL, Docker
- Xây dựng hệ thống thu thập & phân tích 10,000+ sản phẩm từ các sàn TMĐT
- Phát triển ML pipeline: price prediction (MAE < 5%), anomaly detection (F1 > 0.85)
- Thiết kế RESTful API với FastAPI, automated scheduling với APScheduler
- Dashboard real-time với React, hiển thị biến động giá & AI insights
- Triển khai với Docker Compose (5 services), CI/CD pipeline
```

## 6. Demo Flow

1. Người dùng truy cập web → thấy trending products
2. Search sản phẩm → xem lịch sử giá dạng biểu đồ
3. AI gợi ý: "Nên mua" / "Chờ giảm thêm" / "Cảnh báo giá ảo"
4. So sánh giá giữa các sàn
5. Đặt alert → nhận thông báo khi giá giảm
