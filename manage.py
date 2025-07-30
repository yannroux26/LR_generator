#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set!"

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litreview.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print("sys.argv:", sys.argv)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
