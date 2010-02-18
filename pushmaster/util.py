import os

def is_dev():
    try:
        return os.environ['SERVER_SOFTWARE'].startswith('Dev')
    except:
        return False
