import datetime
import re
from defaults import TIMEZONE_SHIFT, DEFAULT_FILE_TYPE, FILE_TYPES


class Message:
    """"""  # TODO - add docstring and type hints
    authors = set()

    def __init__(self, date, author, text):
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


def parse_android_chat(contents):
    """"""  # TODO - add docstring and type hints
    matches = re.findall(
        r'^(\d{2}\/\d{2}\/\d{4}\, \d{1,2}:\d{2}) \- (.*?): (.*)$', contents,
        re.M)
    return [Message(datetime.datetime.strptime(match[0],
                                               '%d/%m/%Y, %H:%M') + TIMEZONE_SHIFT,
                    match[1],
                    match[2])
            for match in matches]


def parse_apple_chat(contents):
    """"""  # TODO - add docstring and type hints
    matches = re.findall(
        r'^(\d{0,2}\/\d{0,2}\/\d{2}\, \d{1,2}:\d{2}) - (.*?): (.*)$', contents,
        re.M)
    return [Message(datetime.datetime.strptime(match[0],
                                               '%m/%d/%y, %H:%M') + TIMEZONE_SHIFT,
                    match[1],
                    match[2])
            for match in matches]


def format_for_pandas(chat):
    """"""  # TODO - add docstring and type hints
    return [{
        'date': item.date,
        'author': item.author,
        'text': item.text,
        'attachment': item.attachmentType() if item.is_attachment() else None
    } for item in chat]


def clean_text(text):
    """"""  # TODO - add docstring and type hints
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


def remove_punctuation(df):
    """"""  # TODO - add docstring and type hints
    punctuations = re.compile('[!"#$%&\'()*+\-./:;<=>?\[\]^_`{|}~]')
    df["text"] = df["text"].replace(punctuations, "", regex=True)
    return df
