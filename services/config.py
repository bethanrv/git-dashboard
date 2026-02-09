import os
import sys
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(ENV_PATH)

def reload_config():
    load_dotenv(ENV_PATH, override=True)

def get_editor():
    return os.getenv("EDITOR_COMMAND", "code")

def get_base_path():
    return os.getenv("BASE_PATH", os.path.expanduser("~/Documents"))

def get_search_depth():
    return int(os.getenv("DEPTH", 1))
