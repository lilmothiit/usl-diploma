from pathlib import Path

# project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DACTYL_DIR = PROJECT_ROOT / ''

DATA_DIR.mkdir(exist_ok=True)

# site
SITE_NAME = 'https://spreadthesign.com'
LANG_PREFIX = 'uk.ua'
ALPHABET_PREFIX = 'alphabet'
