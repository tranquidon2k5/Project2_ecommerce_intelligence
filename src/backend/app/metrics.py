from datetime import datetime


class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.latency_sum = 0.0
        self.latency_count = 0
        self.latency_max = 0.0
        self.started_at = datetime.utcnow()

    def record_request(self, duration_ms: float, status_code: int):
        self.request_count += 1
        self.latency_sum += duration_ms
        self.latency_count += 1
        if duration_ms > self.latency_max:
            self.latency_max = duration_ms
        if status_code >= 500:
            self.error_count += 1

    def get_summary(self) -> dict:
        uptime = (datetime.utcnow() - self.started_at).total_seconds()
        avg_latency = (self.latency_sum / self.latency_count) if self.latency_count > 0 else 0
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        return {
            "uptime_seconds": round(uptime, 0),
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "max_latency_ms": round(self.latency_max, 2),
        }


metrics_collector = MetricsCollector()
