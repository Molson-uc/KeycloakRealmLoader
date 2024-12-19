import requests
import time
import functools


def handle_request_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.HTTPError as e:
            print(f"HTTP Error: {str(e)}")
        except requests.ConnectionError as e:
            print(f"Connection Error: {str(e)}")
        except requests.RequestException as e:
            print(f"Request Exception: {str(e)}")
        except Exception as e:
            print(f"Unexpected Exception: {str(e)}")
        return None

    return wrapper


def delay(delay_ms=0):
    def delay_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(delay_ms / 1000)
            ret = func(*args, **kwargs)
            return ret

        return wrapper

    return delay_decorator
