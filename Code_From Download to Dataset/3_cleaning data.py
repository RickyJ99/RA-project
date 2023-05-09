import pandas as pd

import re


speech_df = pd.read_csv("2_Data_after_infoextraolated.csv", sep=",")


def remove_sentence(text):
    sentence = "\n\n\nShare:\n\n\n\n\nShare on Facebook \n\n\n\nShare on Twitter \n\n\n\nCopy URL to your clipboard \n\n\n\n\n\n\n\t\tAll News\t\n\n\n\n"
    if text.startswith(sentence):
        text = text[len(sentence) :]
    return text


def split_text(text):
    match = re.search(r".Q\s+", text)
    if match:
        split_index = match.start()
        return (text[:split_index], text[split_index + len(match.group()) :])
    else:
        return (text, None)


# pattern = r"James S\. Brady Press Briefing Room \d{1,2}:\d{2} [AP]M\. EDT"


def remove_pattern(text):
    pattern = r"James S\. Brady Press Briefing Room \d{1,2}:\d{2} [AP]M\. EDT"
    new_text = re.sub(pattern, "", text)
    pattern = r"James S\. Brady Press Briefing Room \d{1,2}:\d{2} [AP]M\. EST"
    new_text = re.sub(pattern, "", new_text)
    pattern = r"James S\. Brady Press Briefing Room \d{1,2}:\d{2} [AP]M\."
    new_text = re.sub(pattern, "", new_text)
    pattern = r"Aboard Air Force OneEn Route [A-Za-z\s]+,\s[A-Za-z]+\s*\d{1,2}:\d{2}\s[AP]\.M\. EST"
    new_text = re.sub(pattern, "", new_text)
    pattern = r"James S\. Brady Press Briefing Room\s*\d{1,2}:\d{2}\s[AP]\.M\. EST"
    new_text = re.sub(pattern, "", new_text)
    pattern = r"Via Teleconference\s*\d{1,2}:\d{2}\s[AP]\.M\. EST"
    new_text = re.sub(pattern, "", new_text)
    pattern = r"\n\n\nShare:\n\n\n\n\nShare on Facebook \n\n\n\nShare on Twitter \n\n\n\nCopy URL to your clipboard \n\n\n\n\n\n\n\t\tAll News\t\n\n\n\n"
    new_text = re.sub(pattern, "", new_text)
    pattern = r"Share: Share on Facebook Share on Twitter Copy URL to your clipboard National Security Council All News"
    new_text = re.sub(pattern, "", new_text)
    return new_text


for count in range(len(speech_df["Main text"])):
    # speech_df["Date Time"] = speech_df["Date Time"].str.replace("T", "")

    raw_text = speech_df["Main text"][count]
    raw_text = remove_sentence(raw_text)
    raw_text, speech_df["QA"][count] = split_text(raw_text)
    speech_df["Main text"][count] = remove_pattern(speech_df["Main text"][count])


# Saving the dataset
speech_df.to_csv("3_Data_after_cleaningdata.csv", index=False)
