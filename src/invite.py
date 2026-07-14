
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import pandas as pd
import logging

from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
import os

load_dotenv()

def get_env(key: str, required: bool = True, default=None):
    """
    Fetch an environment variable with clearer failure behavior.
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Missing required environment variable: '{key}'")
    return value

def cred(path: str, scopes: list, subject: str = None):
    """
    Load service account credentials.
    """
    creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
    if subject:
        creds = creds.with_subject(subject)
    return creds


def read_sheet(build, sheet_id: str, range_name: str, creds) -> pd.DataFrame:
    """
    Load exactly one tab from a Google Sheet into a pandas DataFrame.

    Args:
        sheet_id: the spreadsheet ID (from the /d/.../edit URL)
        range_name: the exact tab name, e.g. "nig_student"
        creds: authorized Sheets credentials (readonly scope)
    """
    if not range_name:
        raise ValueError("range_name is required — specify exactly one tab per call")

    try:
        service = build("sheets", "v4", credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

        values = result.get("values", [])
        if not values:
            logging.warning(f"No data found in '{range_name}' (sheet {sheet_id})")
            return pd.DataFrame()

        header, rows = values[0], values[1:]
        header = [h.strip().lower().replace(" ", "_") for h in header]  # normalize
        rows = [r + [None] * (len(header) - len(r)) for r in rows]      # pad ragged rows
        return pd.DataFrame(rows, columns=header)

    except HttpError as e:
        if e.resp.status == 400:
            logging.error(f"Tab '{range_name}' likely doesn't exist in sheet {sheet_id}: {e}")
        else:
            logging.error(f"Sheets API error reading '{range_name}': {e}")
        return pd.DataFrame()

    except Exception as e:
        logging.error(f"Unexpected error loading '{range_name}' from sheet {sheet_id}: {e}")
        return pd.DataFrame()


def invite_student(service, course_id: str, user_email: str, role: str = "STUDENT"):
    """
    Invite a user to a Google Classroom course.
    """
    body = {
        "courseId": course_id,
        "userId": user_email,
        "role": role,
    }

    try:
        invitation = service.invitations().create(body=body).execute()
        logging.info(f"Invitation created: {invitation['id']} for {user_email}")
        return invitation

    except HttpError as e:
        if e.resp.status == 409:
            logging.info(f"Invitation already exists for {user_email} in course {course_id}")
        elif e.resp.status == 404:
            logging.info(f"Course or user not found: {course_id} / {user_email}")
        elif e.resp.status == 400:
            logging.info(f"Bad request — check courseId/role validity: {e}")
        else:
            logging.error(f"Classroom API error: {e}")
        return None



# if __name__ == "__main__":
#     # sheet_id = get_env("de_sheet")   
#     # key_path = get_env("eomo_json_key")
#     # course_id = get_env("de_course")   
#     # analy_json = get_env("analy_js")  

#     # sheet_scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
#     # classroom_scope = ["https://www.googleapis.com/auth/classroom.rosters", "https://www.googleapis.com/auth/classroom.courses.readonly"]

#     # sheet_creds = cred(key_path, sheet_scope)

#     # classroom_creds = cred(analy_json, classroom_scope, subject="ezekiel.sanmabo@dedamdata.org")
#     # classroom_service = build("classroom", "v1", credentials=classroom_creds)

#     # df = read_sheet(sheet_id, 'nig_student', sheet_creds)

#     # for _, row in df.iterrows():          
#     #     if row['payment_details'] == 'paid':   
#     #         invite_student(classroom_service, course_id, row['email'], role='STUDENT')
     