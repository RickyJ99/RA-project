import pandas as pd
import re
import os
import subprocess


def limit_text(text, max_length):
    # Remove irregular characters except punctuation using regular expression
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s\.,;?!\'"\(\)\[\]\{\}<>]', "", text)

    # Limit the text to the maximum length
    limited_text = cleaned_text[:max_length]

    return limited_text


df = pd.read_csv(
    "/Users/riccardodalcero/Library/CloudStorage/OneDrive-UniversitaCattolicaSacroCuore-ICATT/Materials/RA/Data/4_Data_with_AI_Market_Indicies.csv",
    sep=",",
)

df["Date Time"] = pd.to_datetime(df["Date Time"], format="%Y-%m-%d %H:%M:%S%z")


trump_2020 = df[
    (df["Date Time"].dt.year == 2020)
    & (df["Date Time"].dt.month < 9)
    & (df["Title"].str.contains("Press Bri"))
    & (df["Administration"].str.contains("Trump"))
].loc[:, :]

# Create a folder to store the text files
output_folder = "processed_texts"
os.makedirs(output_folder, exist_ok=True)

# Iterate over the dataframe records
for index, row in trump_2020.iterrows():
    # Extract the text from the 'Main text' column
    text = row["Main text"]

    # Preprocess the text by removing irregular characters (except punctuation)
    processed_text = re.sub(r"[^a-zA-Z0-9.,?! ]", "", text)

    # Save the preprocessed text as a separate text file
    file_path = os.path.join(output_folder, f"{index}.txt")
    with open(file_path, "w") as file:
        file.write(processed_text)
