import pandas as pd
import os
from datetime import datetime
from tempfile import NamedTemporaryFile

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.xlsx")

REQUIRED_COLUMNS = ["username", "role", "created_at", "last_login"]

# -------------------------------------------------
# AUTH / AUTO-REGISTRATION
# -------------------------------------------------
def validate_or_register_user(username):
    if not (username.endswith("@bescom.co.in") or username.endswith("@bescom.in")):
        return None, "Unauthorized"

    os.makedirs(DATA_DIR, exist_ok=True)

    if username.endswith("@bescom.in"):
        role = "admin"
    else:
        role = "engineer"
    

    # Load or create dataframe
    if os.path.exists(USERS_FILE):
        df = pd.read_excel(USERS_FILE)
    else:
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Enforce schema safety
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[REQUIRED_COLUMNS]

    # Insert or update user
    if df[df["username"] == username].empty:
        df.loc[len(df)] = {
            "username": username,
            "role": role,
            "created_at": datetime.now(),
            "last_login": datetime.now()
        }
    else:
        df.loc[df["username"] == username, "last_login"] = datetime.now()

    # ✅ ATOMIC WRITE (WINDOWS‑SAFE)
    with NamedTemporaryFile(delete=False, suffix=".xlsx")as tmp:
        temp_path = tmp.name

    df.to_excel(temp_path, index=False)
    os.replace(temp_path, USERS_FILE)

    return role, None
