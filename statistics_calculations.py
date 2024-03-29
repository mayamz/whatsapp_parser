import numpy as np
import pandas as pd
from defaults import *
from parsing_tools import Message
import matplotlib.pyplot as plt

def count_word(df: pd.DataFrame, word: str) -> pd.DataFrame:
    """ Count use of word per author. The word is passed in the form of regex."""
    return df[df["text"].str.contains(r"{}($|\s)".format(word))].groupby(
        "author").count()


def count_haha(df: pd.DataFrame) -> pd.DataFrame:
    """Count how many laugh messages were sent by authors"""
    return df[df["text"].str.contains(r"(^|\W)ח+($|\W)")].groupby("author").count()


def count_emoji(df: pd.DataFrame) -> pd.DataFrame:
    """Count how many emojis were used by each author"""
    return df[df["text"].str.contains(EMOJI_REGEX)].groupby("author").count()


def count_questions(df: pd.DataFrame) -> pd.DataFrame:
    """Count how many questions were asked by each author"""
    return df[df["text"].str.contains(r"\?+")].groupby("author").count()


def count_curses(df: pd.DataFrame) -> pd.DataFrame:
    """count how many curses of each type were used"""
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


def counter_by_user(df: pd.DataFrame, media_df: pd.DataFrame) -> pd.DataFrame:
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

def reverse_hebrew_columns(authors: List[str]) -> Dict[str, str]:
    """ Helper function for plots. Returns a renaming dict for the list given. Revert hebrew names and doesn't change non-hebrew names """
    rename_dict = {}
    for author in authors:
        rename_dict[author] = author if author[0] not in HEBREW_LETTERS else author[::-1]
    return rename_dict

def plot_percentage(counter: pd.DataFrame) -> None:
    """
    generates a horizontal bar plot of each category, and the percentage of each user in it.
    counter is a df that contains the user columns + total column, and indexes of the categories
    """
    # Sort columns alphabetically
    counter = counter[sorted(counter.drop(columns = ["total"]).columns) + ["total"]]

    # reverse hebrew indexes
    counter = counter.rename(index=reverse_hebrew_columns(counter.index))

    # reverse hebrew columns
    counter = counter.rename(columns=reverse_hebrew_columns(counter.columns))

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

def plot_word(df: pd.DataFrame, word: str) -> None:
    """ Counts the use of a specific word by month, and plot by user.
        The word is passed in the form of regex.
    """
    # Take only messages where the word was used
    word_df = df[df["text"].str.contains(r"{}($|\s)".format(word))]

    # Sort columns alphabetically
    word_df = word_df.sort_index(axis=1)

    if word_df.empty:
        print(f"No matches found for {word}")
        return

    # Flip hebrew words to rtl
    if word[0] in HEBREW_LETTERS:
        word = word[::-1]

    # Group by month
    word_df = word_df.groupby([pd.Grouper(freq='M', key='date'), 'author']).count()
    fig, ax = plt.subplots(figsize=(15, 7))
    word_df.unstack().plot(ax=ax)
    plt.ylim(0, plt.ylim()[1])
    plt.title(f"Use Of {word} By User")
    plt.show()

def plot_hhh_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """ Plot a bar graph presenting the amount of h per hhh per user"""
    haha_regex= r"(?:^|\W)(ח+)(?:$|\W)"
    df = df[df["text"].str.contains(haha_regex)]

    haha_df = pd.DataFrame()

    # Get a counter table for each author
    for author in df["author"].unique():
        author_df = df[df["author"]==author]["text"].str.extractall(haha_regex)
        author_df[0] = author_df[0].apply(len)
        author_df = author_df[0].value_counts()

        author_df.name = author
        haha_df = haha_df.merge(author_df, how="outer", left_index = True, right_index = True)

    # Sort columns alphabetically
    haha_df = haha_df.sort_index(axis=1)
    haha_df = haha_df.fillna(0)

    # Plot the histogram
    plot_df = haha_df.rename(columns = reverse_hebrew_columns(haha_df.columns))
    plot_df.plot.bar()
    plt.title("Number of ח in חחח")
    plt.xlabel("Number of ח")
    plt.ylabel("Messages")

    return haha_df