
import pandas as pd
from defaults import EMOJI_REGEX
from parsing_tools import Message


def count_word(df, word, regex=True):
    """"""  # TODO - add docstring and type hints
    """Be careful, word might actually be a regex"""
    return df[df["text"].str.contains(r"{}($|\s)".format(word))].groupby(
        "author").count()


def count_haha(df, regex=True):
    """"""  # TODO - add docstring and type hints
    return df[df["text"].str.contains(r"ח{3,}")].groupby("author").count()


def count_emoji(df):
    """"""  # TODO - add docstring and type hints
    return df[df["text"].str.contains(EMOJI_REGEX)].groupby("author").count()


def count_questions(df, regex=True):
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
    counter = counter.astype(int)

    return counter
