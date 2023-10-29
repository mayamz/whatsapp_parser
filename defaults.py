import datetime
from typing import List, Dict, Tuple, Union, Optional, Any, Callable, Iterable, Set, TypeVar, Generic, Sequence
import pandas as pd

EMOJI_REGEX = "[{}]".format("".join([
    r"\U0001F1E0-\U0001F1FF",  # flags (iOS)
    r"\U0001F300-\U0001F5FF",  # symbols & pictographs
    r"\U0001F600-\U0001F64F",  # emoticons
    r"\U0001F680-\U0001F6FF",  # transport & map symbols
    r"\U0001F700-\U0001F77F",  # alchemical symbols
    r"\U0001F780-\U0001F7FF",  # Geometric Shapes Extended
    r"\U0001F800-\U0001F8FF",  # Supplemental Arrows-C
    r"\U0001F900-\U0001F9FF",  # Supplemental Symbols and Pictographs
    r"\U0001FA00-\U0001FA6F",  # Chess Symbols
    r"\U0001FA70-\U0001FAFF",  # Symbols and Pictographs Extended-A
    r"\U00002702-\U000027B0"  # Dingbats
]))
DEFAULT_FILE_TYPE = 'other'
FILE_TYPES = {
    'aac': 'recording',
    'opus': 'recording',
    'jpg': 'image',
    'mp4': 'video',
    'webp': 'sticker',
    'vcf': 'contact',
}
TIMEZONE_SHIFT = datetime.timedelta(hours=0)  # Thanks Whatsapp

HEBREW_LETTERS = "[אבגדהוזחטיכלמנסעפצקרשתךםןףץ]"

ANDROID_DATES = r'(\d{2}\/\d{2}\/\d{4}\, \d{1,2}:\d{2}) \- (.*?): (.*)$'
APPLE_DATES = r'^(\d{0,2}\/\d{0,2}\/\d{2}\, \d{1,2}:\d{2}) - (.*?): (.*)$'
NEW_FORMAT_DATES = r'^(\d{0,2}\.\d{0,2}\.\d{4}\, \d{1,2}:\d{2}) - (.*?): (.*)$'
DATE_FORMATS = {ANDROID_DATES: '%d/%m/%Y, %H:%M',
                APPLE_DATES: '%m/%d/%y, %H:%M',
                NEW_FORMAT_DATES: '%d.%m.%Y, %H:%M'}
