# backend/app/automation/csv_utils.py

from typing import List
import pandas as pd
from app.log_stream import log

def read_csv_safely(path: str) -> pd.DataFrame:
    log("")
    log("----------------------------------------------")
    log("Step 1 - Reading CSV")
    log(f"CSV path: {path}")
    log("Trying encoding: utf-8-sig (strict)")
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig", encoding_errors="strict")
    except UnicodeDecodeError:
        log("utf-8-sig failed. Trying encoding: latin1 (replace)")
    except Exception as e:
        log(f"utf-8-sig attempt failed: {e}. Trying encoding: latin1 (replace)")

    try:
        return pd.read_csv(path, dtype=str, encoding="latin1", encoding_errors="replace")
    except Exception as e:
        log(f"latin1 failed: {e}. Trying encoding: cp1252 (replace)")

    try:
        return pd.read_csv(path, dtype=str, encoding="cp1252", encoding_errors="replace")
    except Exception as e:
        raise RuntimeError(f"Unable to read CSV with utf-8-sig/latin1/cp1252. Last error: {e}")

def extract_websites(df: pd.DataFrame) -> List[str]:
    log("")
    log("----------------------------------------------")
    log("Step 2 - Normalizing Data")
    df.columns = df.columns.str.strip()
    log(f"Headers: {list(df.columns)}")

    if "website" not in df.columns:
        log("'website' column not found in CSV.")
        return []

    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    log("String columns trimmed.")

    log("")
    log("----------------------------------------------")
    log("Step 3 - Extracting Websites")
    websites = (
        df["website"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"": None})
        .dropna()
        .unique()
        .tolist()
    )
    log(f"Unique websites found: {len(websites)}")
    return websites
