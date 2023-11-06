import os
import pandas as pd

from parsing_tools import *

def read_chat(path: str, name: str) -> pd.DataFrame:
    """ Get path for chats dir and name of chat, reads all the files with same name and concat them """

    files_name = "WhatsApp Chat with " + name
    full_chat = pd.DataFrame()
    files_in_chat = 0

    # Get all files with this name
    for file in os.listdir(path):
        if files_name in file:
            with open(path + file, encoding="utf-8") as f:
                # Update counter
                files_in_chat+=1

                # Read file
                contents = f.read()
                chat = parse_any_format(contents)
                chattext = format_for_pandas(chat)
                df = pd.DataFrame(chattext)

                # Add to full chat
                df["occurrence"] = df.groupby(list(df.columns)).cumcount()
                full_chat = pd.concat([full_chat, df])


    full_chat = full_chat.drop_duplicates().reset_index(drop=True).sort_values("date")
    full_chat = full_chat.drop(columns="occurrence")

    print(f"{files_in_chat} files were found for this chat, they were merged.")

    return full_chat