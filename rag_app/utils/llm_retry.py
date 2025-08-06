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

def extractor_retry_or_none(func):
    '''
    Wrapper for extractor agents:
    retry on rate limit error,
    return None on any other error to continue the flow anyway. None can be changed to the not summarized input if quality matters more than cost.
    '''
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except openai.RateLimitError as e:
                msg = str(e)
                match = re.search(r"try again in ([\d\.]+)s", msg)
                if match:
                    wait_time = float(match.group(1)) + 0.1
                else:
                    wait_time = 2
                print(f"Rate limit reached, waiting {wait_time:.1f}s before retrying...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Extractor agent error: {e}. Returning None.")
                return None
    return wrapper