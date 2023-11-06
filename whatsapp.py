#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bidi.algorithm import get_display
# from PIL import Image
from wordcloud import WordCloud

from read_chat import *
from parsing_tools import *
from statistics_calculations import *
from defaults import HEBREW_LETTERS

def main(path: str, name: str) -> None:
    """ main function, in charge of reading the chat, cleaning it, displaying graphs and printing some statistics """
    df = read_chat(path, name)
    df.head()

    # drop "Media omitted"
    media_df = df[(df["text"] == "<Media omitted>") | (df["text"] == "<המדיה לא נכללה>")]
    df = df[(df["text"] != "<Media omitted>") & (df["text"] != "<המדיה לא נכללה>")]

    print("\n####################\n")

    counter = counter_by_user(df, media_df)
    print("counters by authors")
    print(counter)
    plot_percentage(counter.copy())
    print("\n####################\n")

    hhh_dist = plot_hhh_distribution(df)
    print(hhh_dist)

    print("\n####################\n")
    df = remove_punctuation(df)

    print("curses count")
    curses_counter = count_curses(df)
    print(curses_counter)  # this part works better in notebook, because of the hebrew
    plot_percentage(curses_counter.copy())

    print("\n####################\n")

    print("most common words by author")
    for author in Message.authors:
        authors_words = " ".join(df[df['author'] == author][
                                     "text"]).split()  # Filter here if you want to remove "yes" and whatever
        most_used_words = Counter(authors_words).most_common(5)
        print(author, ":")
        for x in most_used_words:
            print(x[0], " - ", x[1])
        print("\n")

    print("\n####################\n")
    s = input("are you ready for some graphs?")

    # revert hebrew authors for the graphs
    df["author"] = df["author"].mask(df["author"].str.contains(HEBREW_LETTERS), df["author"].str[::-1])

    by_author = df.groupby("author")["text"].count()
    by_author.plot.barh()
    plt.title("messages by author")
    plt.xlabel("messages")
    plt.show()
    df = df.iloc[:, :-1]

    by_month = df.groupby([pd.Grouper(freq='M', key='date'), 'author']).count()
    fig, ax = plt.subplots(figsize=(15, 7))
    by_month.unstack().plot(ax=ax)
    plt.ylim(0, plt.ylim()[1])
    plt.show()

    by_day = \
    df.groupby([((df["date"].dt.weekday + 1) % 7) + 1, 'author']).count()[['text']]
    fig, ax = plt.subplots(figsize=(15, 7))
    by_day.unstack().plot(ax=ax)
    plt.title("by day of the week")
    plt.ylim(0, plt.ylim()[1])
    plt.xlim(1, 7)
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
        # revert name
        if author[::-1] in df["author"].unique():
            author = author[::-1]

        author_text = get_display(clean_text(
            " ".join(text for text in (df[df['author'] == author]["text"]))))
        wordcloud = WordCloud(
            font_path='//C:/Windows/Fonts/calibri.ttf').generate(author_text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(author + "'s word cloud")
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
    path = "/Users/mayam/Downloads/chats/"
    main(path, "תומר של רינת")
