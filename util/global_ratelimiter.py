from requests_ratelimiter import LimiterSession
from config.config import CONFIG

GLOBAL_SESSION = LimiterSession(per_second=CONFIG.REQUESTS_PER_SECOND)
