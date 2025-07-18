import time
from langfuse.openai import openai
import re

def retry_on_rate_limit(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except openai.RateLimitError as e:
                # Try to extract recommended wait time from error message
                msg = str(e)
                match = re.search(r"try again in ([\d\.]+)s", msg)
                if match:
                    wait_time = float(match.group(1)) + 0.1  # add a small buffer
                else:
                    wait_time = 2
                print(f"Rate limit reached, waiting {wait_time:.1f}s before retrying...")
                time.sleep(wait_time)
    return wrapper