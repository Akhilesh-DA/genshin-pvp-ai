# ============================================================
# GENSHIN IMPACT PVP AI
# Data Loading and Preprocessing Module
# ============================================================

import os
import pandas as pd
import numpy as np

import config


# ------------------------------------------------------------
# LOAD DATASET
# ------------------------------------------------------------

def load_dataset(file_path=None):
    """
    Load the Genshin Impact character dataset.

    The default dataset is:

        data/genshin_impact.csv

    Returns
    -------
    pandas.DataFrame
        Loaded character dataset.
    """

    if file_path is None:
        file_path = config.CSV_FILE

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"\nDataset not found:\n{file_path}\n\n"
            "Make sure genshin_impact.csv is inside "
            "the data folder."
        )

    print("\n========================================")
    print("        LOADING GENSHIN DATASET")
    print("========================================")

    print(f"\nDataset: {file_path}")

    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    df = pd.read_csv(file_path)

    print("\nDataset loaded successfully.")

    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    return df


# ------------------------------------------------------------
# CLEAN COLUMN NAMES
# ------------------------------------------------------------

def clean_column_names(df):
    """
    Standardize column names.

    Example:

        Character Name
        ↓
        character_name

    This makes the dataset easier for the
    other modules to use.
    """

    df = df.copy()

    cleaned_columns = []

    for column in df.columns:

        column = str(column)

        column = column.strip()

        column = column.lower()

        column = column.replace(" ", "_")

        column = column.replace("-", "_")

        column = column.replace("/", "_")

        column = column.replace("(", "")

        column = column.replace(")", "")

        cleaned_columns.append(column)

    df.columns = cleaned_columns

    return df


# ------------------------------------------------------------
# REMOVE DUPLICATES
# ------------------------------------------------------------

def remove_duplicates(df):
    """
    Remove completely duplicated rows.
    """

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    removed = before - after

    if removed > 0:

        print(
            f"\nRemoved {removed} duplicate rows."
        )

    return df


# ------------------------------------------------------------
# HANDLE MISSING VALUES
# ------------------------------------------------------------

def handle_missing_values(df):
    """
    Handle missing values.

    Numeric columns:
        Missing values are replaced by the median.

    Text columns:
        Missing values are replaced by 'Unknown'.
    """

    df = df.copy()

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    text_columns = df.select_dtypes(
        exclude=np.number
    ).columns

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    for column in numeric_columns:

        if df[column].isnull().sum() > 0:

            median_value = df[column].median()

            df[column] = df[column].fillna(
                median_value
            )

    # --------------------------------------------------------
    # Text columns
    # --------------------------------------------------------

    for column in text_columns:

        if df[column].isnull().sum() > 0:

            df[column] = df[column].fillna(
                "Unknown"
            )

    return df


# ------------------------------------------------------------
# CONVERT NUMERIC COLUMNS
# ------------------------------------------------------------

def convert_numeric_columns(df):
    """
    Attempt to convert columns containing
    mostly numerical values into numeric format.
    """

    df = df.copy()

    for column in df.columns:

        if df[column].dtype == "object":

            converted = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            valid_ratio = (
                converted.notna().mean()
            )

            # If at least 80% of the values are
            # numeric, treat the column as numeric.

            if valid_ratio >= 0.80:

                df[column] = converted

    return df


# ------------------------------------------------------------
# IDENTIFY IMPORTANT COLUMNS
# ------------------------------------------------------------

def identify_columns(df):
    """
    Identify commonly useful character columns.

    Different datasets may use different names,
    so multiple possible names are checked.
    """

    column_mapping = {}

    # --------------------------------------------------------
    # Character name
    # --------------------------------------------------------

    name_candidates = [

        "name",

        "character_name",

        "character",

        "char_name"

    ]

    # --------------------------------------------------------
    # Element
    # --------------------------------------------------------

    element_candidates = [

        "element",

        "vision",

        "element_type"

    ]

    # --------------------------------------------------------
    # Weapon
    # --------------------------------------------------------

    weapon_candidates = [

        "weapon",

        "weapon_type",

        "weapon_class"

    ]

    # --------------------------------------------------------
    # Rarity
    # --------------------------------------------------------

    rarity_candidates = [

        "rarity",

        "stars",

        "star",

        "rarity_stars"

    ]

    # --------------------------------------------------------
    # Search helper
    # --------------------------------------------------------

    def find_column(candidates):

        for candidate in candidates:

            if candidate in df.columns:

                return candidate

        return None

    column_mapping["name"] = find_column(
        name_candidates
    )

    column_mapping["element"] = find_column(
        element_candidates
    )

    column_mapping["weapon"] = find_column(
        weapon_candidates
    )

    column_mapping["rarity"] = find_column(
        rarity_candidates
    )

    return column_mapping


# ------------------------------------------------------------
# CREATE CHARACTER ID
# ------------------------------------------------------------

def create_character_id(df, column_mapping):
    """
    Create a unique identifier for every character.
    """

    df = df.copy()

    name_column = column_mapping.get(
        "name"
    )

    if name_column is not None:

        df["character_id"] = (

            df[name_column]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(
                " ",
                "_",
                regex=False
            )

        )

    else:

        df["character_id"] = [

            f"character_{i}"

            for i in range(len(df))

        ]

    return df


# ------------------------------------------------------------
# CREATE BASIC PVP FEATURES
# ------------------------------------------------------------

def create_basic_features(df):
    """
    Create standardized PvP statistics.

    The function searches for common HP, ATK
    and DEF column names in the dataset.

    If a statistic does not exist, a neutral
    default value is used.
    """

    df = df.copy()

    # --------------------------------------------------------
    # POSSIBLE HP COLUMNS
    # --------------------------------------------------------

    hp_columns = [

        "hp",

        "base_hp",

        "lvl_90_hp",

        "level_90_hp",

        "hp_90"

    ]

    # --------------------------------------------------------
    # POSSIBLE ATK COLUMNS
    # --------------------------------------------------------

    atk_columns = [

        "atk",

        "attack",

        "base_atk",

        "lvl_90_atk",

        "level_90_atk",

        "atk_90"

    ]

    # --------------------------------------------------------
    # POSSIBLE DEF COLUMNS
    # --------------------------------------------------------

    def_columns = [

        "def",

        "defense",

        "base_def",

        "lvl_90_def",

        "level_90_def",

        "def_90"

    ]

    # --------------------------------------------------------
    # FIND NUMERIC COLUMN
    # --------------------------------------------------------

    def find_numeric_column(candidates):

        for candidate in candidates:

            if candidate in df.columns:

                if pd.api.types.is_numeric_dtype(
                    df[candidate]
                ):

                    return candidate

        return None

    hp_column = find_numeric_column(
        hp_columns
    )

    atk_column = find_numeric_column(
        atk_columns
    )

    def_column = find_numeric_column(
        def_columns
    )

    # --------------------------------------------------------
    # CREATE STANDARDIZED HP
    # --------------------------------------------------------

    if hp_column is not None:

        df["pvp_hp"] = (
            df[hp_column]
            .astype(float)
        )

    else:

        df["pvp_hp"] = 1000.0

    # --------------------------------------------------------
    # CREATE STANDARDIZED ATK
    # --------------------------------------------------------

    if atk_column is not None:

        df["pvp_atk"] = (
            df[atk_column]
            .astype(float)
        )

    else:

        df["pvp_atk"] = 100.0

    # --------------------------------------------------------
    # CREATE STANDARDIZED DEF
    # --------------------------------------------------------

    if def_column is not None:

        df["pvp_def"] = (
            df[def_column]
            .astype(float)
        )

    else:

        df["pvp_def"] = 100.0

    return df


# ------------------------------------------------------------
# NORMALIZE STATISTICS
# ------------------------------------------------------------

def normalize_stats(df):
    """
    Normalize HP, ATK and DEF between 0 and 1.
    """

    df = df.copy()

    stat_columns = [

        "pvp_hp",

        "pvp_atk",

        "pvp_def"

    ]

    for column in stat_columns:

        if column not in df.columns:

            continue

        minimum = df[column].min()

        maximum = df[column].max()

        if maximum != minimum:

            df[column + "_normalized"] = (

                (df[column] - minimum)
                /
                (maximum - minimum)

            )

        else:

            df[column + "_normalized"] = 0.5

    return df


# ------------------------------------------------------------
# COMPLETE PREPROCESSING
# ------------------------------------------------------------

def preprocess_dataset(df):
    """
    Run all preprocessing steps.
    """

    print("\n========================================")
    print("        PREPROCESSING DATA")
    print("========================================")

    # 1. Clean column names
    df = clean_column_names(df)

    # 2. Remove duplicate rows
    df = remove_duplicates(df)

    # 3. Convert numeric values
    df = convert_numeric_columns(df)

    # 4. Handle missing values
    df = handle_missing_values(df)

    # 5. Identify important columns
    column_mapping = identify_columns(df)

    print("\nDetected columns:")

    for key, value in column_mapping.items():

        print(
            f"  {key:<10} : {value}"
        )

    # 6. Create character IDs
    df = create_character_id(
        df,
        column_mapping
    )

    # 7. Create standardized PvP statistics
    df = create_basic_features(df)

    # 8. Normalize statistics
    df = normalize_stats(df)

    print(
        "\nPreprocessing completed."
    )

    return df, column_mapping


# ------------------------------------------------------------
# SAVE PROCESSED DATA
# ------------------------------------------------------------

def save_processed_data(
    df,
    file_path=None
):
    """
    Save the processed dataset.
    """

    if file_path is None:

        file_path = config.PROCESSED_DATA

    directory = os.path.dirname(
        file_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    df.to_csv(
        file_path,
        index=False
    )

    print(
        "\nProcessed dataset saved to:"
    )

    print(
        file_path
    )


# ------------------------------------------------------------
# COMPLETE DATA PIPELINE
# ------------------------------------------------------------

def load_and_prepare_data(
    file_path=None
):
    """
    Main data pipeline.

    This function will be called by other
    modules in the project.
    """

    # Load raw dataset
    df = load_dataset(
        file_path
    )

    # Preprocess dataset
    df, column_mapping = (
        preprocess_dataset(df)
    )

    # Save processed version
    save_processed_data(
        df
    )

    return df, column_mapping


# ------------------------------------------------------------
# TEST THE MODULE DIRECTLY
# ------------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        " GENSHIN PVP AI - DATA LOADER TEST"
    )

    print(
        "========================================"
    )

    try:

        df, mapping = (
            load_and_prepare_data()
        )

        print(
            "\n----------------------------------------"
        )

        print(
            "FIRST 5 ROWS"
        )

        print(
            "----------------------------------------"
        )

        print(
            df.head()
        )

        print(
            "\n----------------------------------------"
        )

        print(
            "FINAL COLUMNS"
        )

        print(
            "----------------------------------------"
        )

        for column in df.columns:

            print(
                f"  {column}"
            )

        print(
            "\n----------------------------------------"
        )

        print(
            "DATA LOADER TEST SUCCESSFUL"
        )

        print(
            "----------------------------------------"
        )

    except Exception as error:

        print(
            "\n----------------------------------------"
        )

        print(
            "DATA LOADER ERROR"
        )

        print(
            "----------------------------------------"
        )

        print(
            error
        )