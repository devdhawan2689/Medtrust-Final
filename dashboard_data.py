import sqlite3
import pandas as pd
import numpy as np

def fetch_patient_data(aadhaar_number):
    # Connect to the database
    conn = sqlite3.connect("aadhaar_data.db")

    # Example UID (replace with the UID you want to search)
    uid_to_search = aadhaar_number

    # Query with parameterized input (to avoid SQL injection)
    query = """
    SELECT "Full Name",
    subject_id,
    gender,
    dob
    FROM UID_DATA
    WHERE UID = ?;
    """

    # Fetch into DataFrame
    df = pd.read_sql_query(query, conn, params=(uid_to_search,))

    # Show the result
    # print(df)

    # Close connection
    conn.close() 

    return df 

def fetch_admissions_data(subject_id):
    db_path = "MedTrustPatientData.sqlite"  # change if needed
    conn = sqlite3.connect(db_path)

    # Fetch data
    df = pd.read_sql_query(
        "SELECT admittime, admission_type FROM admissions WHERE subject_id = ?;",
        conn,
        params=(subject_id,)
    )

    # Convert to datetime
    df["admittime"] = pd.to_datetime(df["admittime"])

    # Sort and get the most recent
    df = df.sort_values(by="admittime", ascending=False).reset_index(drop=True)

    # Most recent admittime
    most_recent = df.iloc[0]["admittime"] if not df.empty else None

    print("Most recent admittime:", most_recent)

    conn.close() 

    return df  

def fetch_icustays_data(subject_id):
    db_path = "MedTrustPatientData.sqlite"  # change if needed
    conn = sqlite3.connect(db_path)

    subject_id = 10006  # example

    # Query icustays with intime and los
    df = pd.read_sql_query(
        "SELECT intime, los FROM icustays WHERE subject_id = ?;",
        conn,
        params=(subject_id,)
    )

    if not df.empty:
        # Convert intime to datetime
        df["intime"] = pd.to_datetime(df["intime"])
        
        # Get the most recent intime
        df = df.sort_values(by="intime", ascending=False).head(1).reset_index(drop=True)
        df["ICU"] = "Yes"
    else:
        df = pd.DataFrame({"intime": [pd.NaT], "los": [np.nan], "ICU": ["No"]})

    # print(df)

    conn.close()

    return df  