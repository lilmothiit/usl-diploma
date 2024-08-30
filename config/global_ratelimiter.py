from requests_ratelimiter import LimiterSession
GLOBAL_SESSION = LimiterSession(per_second=5)