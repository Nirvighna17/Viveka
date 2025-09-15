import pandas as pd
import os
from rapidfuzz import process, fuzz

# -------------------------------
# Load Database (CSV → DataFrame)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
DATA_PATH = os.path.join(BASE_DIR, "data", "items.csv")

try:
    df = pd.read_csv(DATA_PATH)
    # Clean column names
    df.rename(columns=lambda x: x.strip(), inplace=True)

    # Ensure 'Ingredient' column exists
    if 'Ingredient' not in df.columns:
        # Assume first column is ingredient name
        df.rename(columns={df.columns[0]: 'Ingredient'}, inplace=True)

    print(f"Loaded {len(df)} ingredients from {DATA_PATH}")
except FileNotFoundError:
    print(f"ERROR: File not found at {DATA_PATH}")
    df = pd.DataFrame()  # Empty dataframe as fallback

# -------------------------------
# Matcher Function
# -------------------------------
def match_ingredients(text_list, df, threshold=80):
    """
    Match extracted text to ingredients DB using fuzzy matching.
    :param text_list: List of strings (OCR output or manual input)
    :param df: DataFrame of ingredients
    :param threshold: Match confidence threshold (default 80)
    :return: List of matched ingredient dicts
    """
    matched_items = []
    if df.empty or 'Ingredient' not in df.columns:
        return matched_items

    for word in text_list:
        match = process.extractOne(word, df['Ingredient'], scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:
            ingredient_info = df[df['Ingredient'] == match[0]].to_dict('records')[0]
            matched_items.append(ingredient_info)
    return matched_items


