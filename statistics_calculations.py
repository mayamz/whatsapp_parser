import numpy as np
import pandas as pd
from defaults import EMOJI_REGEX, HEBREW_LETTERS
from parsing_tools import Message
import matplotlib.pyplot as plt

def count_word(df, word):
    """"""  # TODO - add docstring and type hints
    """ Count use of word per author. The word is passed in the form of regex."""
    return df[df["text"].str.contains(r"{}($|\s)".format(word))].groupby(
        "author").count()


def count_haha(df):
    """"""  # TODO - add docstring and type hints
    return df[df["text"].str.contains(r"ח{3,}")].groupby("author").count()


def count_emoji(df):
    """"""  # TODO - add docstring and type hints
    return df[df["text"].str.contains(EMOJI_REGEX)].groupby("author").count()


def count_questions(df):
    """"""  # TODO - add docstring and type hints
    return df[df["text"].str.contains(r"\?+")].groupby("author").count()


def count_curses(df):
    """"""  # TODO - add docstring and type hints
    counter = pd.DataFrame()
    curse_list = ["פאק", "פאקינג", "שיט", "סעמק", "כוסאמק", "זונה", "דמט",
                  "דאם", "דאמ", "לעזאזל", "זין", "רבאק"]
    for curse in curse_list:
        curse_row = pd.DataFrame()
        # generate the regex that allows letter repetitions
        curse_regex = ""
        for letter in curse:
            curse_regex = curse_regex + letter + "+"

        curse_row[curse] = count_word(df, curse_regex).iloc[:, 1]
        counter = pd.concat([counter, curse_row], axis=1)
    counter["total"] = counter.sum(axis=1) # total per author
    counter = counter.fillna(0)
    counter = counter.transpose()
    counter["total"] = counter.sum(axis=1) # total per curse
    counter = counter.astype(int)

    return counter


def counter_by_user(df, media_df):
    """
    all the counters in one df
    currently: messages, words, hhh, emoji, questions
    all by authors
    """
    counter = pd.DataFrame()
    counter["messages"] = df.groupby("author").count().iloc[:, 1]
    counter["media"] = media_df.groupby("author").count().iloc[:, 1]
    counter["words"] = None
    for author in Message.authors:
        authors_words = " ".join(df[df['author'] == author][
                                     "text"]).split()  # Filter here if you want to remove "yes" and whatever
        counter.loc[author, "words"] = len(authors_words)

    counter["hhh"] = count_haha(df).iloc[:, 1]
    counter["emoji"] = count_emoji(df).iloc[:, 1]
    counter["questions"] = count_questions(df).iloc[:, 1]
    counter["keilu"] = count_word(df, "כאילו").iloc[:, 1]
    counter = counter.transpose()
    counter["total"] = counter.sum(axis=1)
    counter = counter.fillna(0)
    counter = counter.astype(int)

    return counter

def plot_percentage(counter):
    """
    generates a horizontal bar plot of each category, and the percentage of each user in it.
    counter is a df that contains the user columns + total column, and indexes of the categories
    """

    # reverse hebrew indexes
    counter.index = counter.index.where(~counter.index.str.contains(HEBREW_LETTERS), counter.index.str[::-1])

    # reverse hebrew columns
    counter.columns = counter.columns.where(~counter.columns.str.contains(HEBREW_LETTERS), counter.columns.str[::-1])

    # change counters to percentages
    for col in counter.columns[:-1]:
            counter[col] = counter[col].mask(counter["total"]!=0, counter[col] / counter["total"] * 100)

    fig, ax = plt.subplots()
    fig.set_figheight(len(counter) * 0.6)

    # generates the first bar (starts with 0)
    ax.barh(counter.index, counter.iloc[:,0], label=counter.columns[0])
    for user in range(1, len(counter.columns)-1):
        ax.barh(counter.index, counter.iloc[:,user], height=0.8, left=counter.iloc[:,:user].sum(axis=1), label=counter.columns[user])

    for p in ax.patches:
        txt = str(p.get_width().round(1)) + '%'

        # locations for two users (two ends)
        if len(counter.columns)==3:
            if p.get_x() == 0:
                txt_x = 0
            else:
                txt_x = 90
        # if more - left side of bar
        else:
            txt_x = p.get_x()
        txt_y = p.get_y()+0.4
        ax.text(txt_x, txt_y, txt)

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlim(0,100)
    plt.show()

def plot_word(df, word):
    """ Counts the use of a specific word by month, and plot by user.
        The word is passed in the form of regex.
    """
    by_month = df[df["text"].str.contains(r"{}($|\s)".format(word))]

    if not len(by_month):
        print(f"No matches found for {word}")
        return

    if word[0] in HEBREW_LETTERS:
        word = word[::-1]

    by_month = by_month.groupby([pd.Grouper(freq='M', key='date'), 'author']).count()
    fig, ax = plt.subplots(figsize=(15, 7))
    by_month.unstack().plot(ax=ax)
    plt.ylim(0, plt.ylim()[1])
    plt.title(f"Use Of {word} By User")
    plt.show()