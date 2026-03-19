import random
from fake_useragent import UserAgent


DESKTOP_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


class RandomUserAgentMiddleware:
    """Rotate User-Agent for each request."""

    def __init__(self):
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None

    def process_request(self, request, spider):
        if self.ua:
            try:
                request.headers["User-Agent"] = self.ua.random
                return
            except Exception:
                pass
        request.headers["User-Agent"] = random.choice(DESKTOP_AGENTS)
