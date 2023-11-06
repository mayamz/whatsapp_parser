import datetime
import re
from defaults import *


class Message:
    """
    A class representing a single message in the chat.
    """
    authors: Set[str] = set()

    def __init__(self, date: datetime.datetime, author: str, text: str):
        self.date = date
        self.author = author
        self.text = text
        self.authors.add(self.author)

    def is_attachment(self):
        return self.text.startswith(
            "\u200e<attached: ") and self.text.endswith(">")

    def attachment_extension(self):
        assert self.is_attachment(), "Not an attachment, too bad"
        return self.text[self.text.rfind(".") + 1:-1]

    def is_omitted(self):
        return self.text.startswith("\u200e<") and self.text.endswith(
            "Media omitted>")

    def omitted_extension(self):
        assert self.is_omitted(), "Not omitted, too bad"
        return 'omt'

    def attachment_type(self):
        ext = self.omitted_extension()
        if ext in FILE_TYPES:
            return FILE_TYPES[ext]
        return DEFAULT_FILE_TYPE


def parse_any_format(contents: str) -> List[Message]:
    """
    Parse the chat, regardless of date format
    Parameters
    ----------
    contents: str - the contents of the chat file

    Raises
    ------
    Exception - if the format is not known
    """
    for format in DATE_FORMATS:
        if re.search(format, contents, re.M):
            matches = re.findall(format, contents, re.M)
            return [Message(datetime.datetime.strptime(match[0], DATE_FORMATS[format]) + TIMEZONE_SHIFT,
                            match[1], match[2]) for match in matches]
    raise Exception("Not a known format")

def format_for_pandas(chat: List[Message]) -> List[Dict[str, Any]]:
    """
    Format the chat for pandas DataFrame creation

    Parameters
    ----------
    chat: List[Message] - the chat to format
    """
    return [{
        'date': item.date,
        'author': item.author,
        'text': item.text,
        'attachment': item.attachment_type() if item.is_attachment() else None
    } for item in chat]


def clean_text(text: str) -> str:
    """
    Remove emojis and other weird characters from text
    Parameters
    ----------
    text: str - the text to clean
    """
    weirdPatterns = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u'\U00010000-\U0010ffff'
                               u"\u200d"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\u3030"
                               u"\ufe0f"
                               u"\u2069"
                               u"\u2066"
                               u"\u200c"
                               u"\u2068"
                               u"\u2067"
                               "]+", flags=re.UNICODE)
    clean_text = weirdPatterns.sub(r'', text)
    return (clean_text)


def remove_punctuation(df: pd.DataFrame) -> pd.DataFrame:
    """ Remove punctuation from text column in df"""
    punctuations = re.compile('[!"#$%&\'()*+\-./:;<=>?\[\]^_`{|}~]')
    df["text"] = df["text"].replace(punctuations, "", regex=True)
    return df
