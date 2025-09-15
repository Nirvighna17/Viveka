import streamlit as st
import pandas as pd


# -------------------------------
# Analyzer Function
# -------------------------------
def analyze_ingredients(matched_items):
    """
    Prepare ingredient info for display in user-friendly format.
    :param matched_items: List of dicts from matcher
    :return: DataFrame ready for Streamlit display
    """
    if not matched_items:
        return pd.DataFrame(columns=["Ingredient", "Category", "Side Effects", "Prescription Required"])

    data = []
    for item in matched_items:
        # Convert technical terms to common terms (example mapping)
        side_effects = item.get("Possible Side Effects", "None")
        category = item.get("Category", "Unknown")
        prescription = item.get("Prescription Required", "No")

        # You can expand this mapping for layman terms
        side_effects_mapping = {
            "Minimal": "Generally safe",
            "Stomach upset": "May cause stomach issues",
            "Allergic reactions": "Can cause allergy",
            "Obesity": "May contribute to weight gain",
            "High sodium": "High salt content",
            "High cholesterol": "May raise cholesterol"
        }
        side_effects_friendly = side_effects_mapping.get(side_effects, side_effects)

        data.append({
            "Ingredient": item.get("Ingredient", ""),
            "Category": category,
            "Side Effects": side_effects_friendly,
            "Prescription Required": prescription
        })

    df = pd.DataFrame(data)
    return df


# -------------------------------
# Streamlit Display Function
# -------------------------------
def display_analysis(df):
    """
    Display ingredient analysis in Streamlit with manual edit option.
    :param df: DataFrame from analyze_ingredients
    """
    st.subheader("Matched Ingredients Analysis")

    if df.empty:
        st.info("No ingredients matched.")
        return df

    # Editable table
    edited_df = st.data_editor(df, num_rows="dynamic")

    # Optionally, return edited df for further processing
    return edited_df


# -------------------------------
# Test / Standalone Run
# -------------------------------
if __name__ == "__main__":
    # Simulate matched items from matcher.py
    matched_items = [
        {"Ingredient": "Sodium Benzoate", "Category": "Preservative", "Possible Side Effects": "Allergic reactions",
         "Prescription Required": "No"},
        {"Ingredient": "Aspartame", "Category": "Artificial Sweetener", "Possible Side Effects": "Headache",
         "Prescription Required": "No"},
        {"Ingredient": "MSG", "Category": "Food Additive", "Possible Side Effects": "Headache/Allergic reactions",
         "Prescription Required": "No"}
    ]

    df = analyze_ingredients(matched_items)
    print(df)

    # If running in Streamlit
    # st.write(display_analysis(df))
