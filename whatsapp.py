#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime
import pandas as pd
import numpy as np
from collections import Counter
from bidi.algorithm import get_display

from os import path
#from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt



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


class Message:
    authors = set()
    def __init__(self, date, author, text):
        self.date = date
        self.author = author
        self.text = text
        self.authors.add(self.author)

    def isAttachment(self):
        return self.text.startswith("\u200e<attached: ") and self.text.endswith(">")

    def attachmentExtension(self):
        assert self.isAttachment(), "Not an attachment, too bad"
        return self.text[self.text.rfind(".") + 1:-1]

    def isOmitted(self):
        return self.text.startswith("\u200e<") and self.text.endswith("Media omitted>")

    def omitteExtension(self):
        assert self.isOmitted(), "Not omitted, too bad"
        return 'omt'

    def attachmentType(self):
        ext = self.attachmentExtension()
        if ext in FILE_TYPES:
            return FILE_TYPES[ext]
        return DEFAULT_FILE_TYPE

def parse_android_chat(contents):
    matches = re.findall(r'^(\d{2}\/\d{2}\/\d{4}\, \d{1,2}:\d{2}) \- (.*?): (.*)$', contents, re.M)
    return [Message(datetime.datetime.strptime(match[0], '%d/%m/%Y, %H:%M') + TIMEZONE_SHIFT,
                    match[1],
                    match[2])
            for match in matches]

def parse_apple_chat(contents):
    matches = re.findall(r'^(\d{0,2}\/\d{0,2}\/\d{2}\, \d{1,2}:\d{2}) - (.*?): (.*)$', contents,
                         re.M)
    return [Message(datetime.datetime.strptime(match[0], '%m/%d/%y, %H:%M') + TIMEZONE_SHIFT,
                    match[1],
                    match[2])
            for match in matches]

def format_for_pandas(chat):
    return [{
        'date': item.date,
        'author': item.author,
        'text': item.text,
        'attachment': item.attachmentType() if item.isAttachment() else None
    } for item in chat]

def count_word(df, word, regex=True):
    """Be careful, word might actually be a regex"""
    return df[df["text"].str.contains(r"{}($|\s)".format(word))].groupby("author").count()

def count_haha(df, regex=True):
    return df[df["text"].str.contains(r"ח{3,}")].groupby("author").count()

def count_emoji(df):
    return df[df["text"].str.contains(EMOJI_REGEX)].groupby("author").count()

def count_questions(df, regex=True):
    return df[df["text"].str.contains(r"\?+")].groupby("author").count()

def count_curses(df):
    counter = pd.DataFrame()
    curse_list = ["פאק", "שיט", "סעמק", "זונה", "דמט", "דאם", "דאמ", "לעזאזל", "זין", "רבאק"]
    for curse in curse_list:
        curse_row = pd.DataFrame()
        # generate the regex that allows letter repetitions
        curse_regex = ""
        for letter in curse:
            curse_regex = curse_regex+letter+"+"

        curse_row[curse] = count_word(df,curse_regex).iloc[:,1]
        counter = pd.concat([counter,curse_row],axis=1)
    counter["total"] = counter.sum(axis=1)
    counter = counter.fillna(0)
    counter = counter.transpose()
    return counter

def counter_by_user(df):
    ''' all the counters in one df
        currently: messages, words, hhh, emoji, questions
        all by authors
        '''
    counter = pd.DataFrame()
    counter["messages"] = df.groupby("author").count().iloc[:,1]
    counter["words"] = None
    for author in Message.authors:
        authors_words = " ".join(df[df['author'] == author]["text"]).split()  # Filter here if you want to remove "yes" and whatever
        counter.loc[author,"words"] = len(authors_words)

    counter["hhh"] = count_haha(df).iloc[:,1]
    counter["emoji"] = count_emoji(df).iloc[:,1]
    counter["questions"] = count_questions(df).iloc[:,1]
    counter["keilu"] = count_word(df,"כאילו").iloc[:,1]
    counter = counter.transpose()

    return counter

def clean_text(text):
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
    punctuations = re.compile('[!"#$%&\'()*+\-./:;<=>?\[\]^_`{|}~]')
    df["text"] = df["text"].replace(punctuations,"",regex=True)
    return df

def main(path,name):
    with open(path+name+".txt", encoding="utf-8") as f:
        contents = f.read()

    if re.search(r'^(\d{0,2}\/\d{0,2}\/\d{2}\, \d{1,2}:\d{2}) - (.*?): (.*)$', contents,re.M):
        chat = parse_apple_chat(contents)
    else:
        chat = parse_android_chat(contents)

    chattext = format_for_pandas(chat)
    df = pd.DataFrame(chattext)
    df.head()

    # drop "Media omitted"
    df = df[df["text"]!="<Media omitted>"]


    """
    print ("how many attachments")
    attachment_counts = df.groupby(["author", "attachment"]).count()
    print(attachment_counts)

    print("\n####################\n")
    """

    counter = counter_by_user(df)
    print ("counters by authors")
    print (counter)

    print("\n####################\n")
    df = remove_punctuation(df)

    print("curses count")
    curses_counter = count_curses(df)
    print(curses_counter) # this part works better in notebook, because of the hebrew

    print("\n####################\n")

    print ("most common words by author")
    for author in Message.authors:
        authors_words = " ".join(df[df['author'] == author]["text"]).split()  # Filter here if you want to remove "yes" and whatever
        most_used_words = Counter(authors_words).most_common(5)
        print (author,":")
        for x in most_used_words:
            print (x[0]," - ", x[1])
        print ("\n")

    print ("\n####################\n")
    s = input("are you ready for some graphs?")

    by_author.plot.barh()
    plt.title("messages by author")
    plt.show()
    df = df.iloc[:,:-1]

    by_month = df.groupby([pd.Grouper(freq='M', key='date'), 'author']).count()
    fig, ax = plt.subplots(figsize=(15, 7))
    by_month.unstack().plot(ax=ax)
    plt.ylim(0, plt.ylim()[1])
    plt.show()

    by_day = df.groupby([((df["date"].dt.weekday+1)%7)+1, 'author']).count()[['text']]
    fig, ax = plt.subplots(figsize=(15, 7))
    by_day.unstack().plot(ax=ax)
    plt.title("by day of the week")
    plt.ylim(0, plt.ylim()[1])
    plt.xlim(1,7)
    plt.show()

    by_hour = df.groupby([df["date"].dt.hour, 'author']).count()[['text']]
    fig, ax = plt.subplots(figsize=(15, 7))
    by_hour.unstack().plot(ax=ax)
    plt.xlabel("hour")
    plt.xticks(np.arange(0, 24, 1))
    plt.xlim(0, 23)
    plt.ylim(0, plt.ylim()[1])
    plt.title("by hour")
    plt.show()

    """Create and generate a word cloud image:"""
    ax.get_legend().remove()
    for author in Message.authors:
        author_text = get_display(clean_text(" ".join(text for text in (df[df['author'] == author]["text"]))))
        wordcloud = WordCloud(font_path='//C:/Windows/Fonts/calibri.ttf').generate(author_text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(author+"'s word cloud")
        plt.axis("off")
        plt.show()

    """
    bidi_text = get_display(adi_text)
    wordcloud = WordCloud(font_path='//C:/Windows/Fonts/calibri.ttf').generate(bidi_text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title("adi's word cloud")
    plt.axis("off")
    plt.show()
    """


    # that was me trying all kinds of things and ultimately failing
    # print(df.describe())
    # df['Day of Week'] = df['Date'].apply(lambda time: time.day_name())
    # sender_count = df['Author'].value_counts()
    # print(sender_count)
    # emoji_df = df[df['Text'].str.
    #     contains(r'[^0-9,/:\[\]\u200e\n\u200f\r\t .?<>\-"\'!@#$%^&*\(\)_=+\f§;{}\u0590-\u05FF\uFB2A-\uFB4Ea-zA-Zא-ת]')]
    # print(emoji_df.describe())
    # most_sent_emoji = emoji_df["Author" == "רינת"].Text.mode()
    # print(most_sent_emoji)
    # # df['Word_Count'] = df['Text'].apply(lambda s: len(s.split(' ')))

    # sender_count.plot.barh()

    # ... Profit?


if __name__ == "__main__":
    path = "/Users/mayam/Downloads/chats/WhatsApp Chat with "
    main(path, "תומר של רינת")

