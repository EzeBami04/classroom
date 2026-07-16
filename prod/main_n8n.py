import sys
import logging
from googleapiclient.discovery import build
from src.invite import read_sheet, invite_student, cred, get_env

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

#============= Set up  environment variables ============

SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
CLASSROOM_SCOPE = [
    "https://www.googleapis.com/auth/classroom.rosters",
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    ]


#=======================================================
def main():
    sheet_id = get_env("n8n_sheet")
    sheet_key_path = get_env("eomo_json_key")
    classroom_key_path = get_env("analy_js")
    course_id = get_env("n8n_course")
    IMPERSONATE_AS = get_env("IMPERSONATE_AS")

    logging.info("Fetching student information from sheet")
    sheet_creds = cred(sheet_key_path, SHEET_SCOPE)

    logging.info("Authenticating with Classroom")
    classroom_creds = cred(classroom_key_path, CLASSROOM_SCOPE, subject=IMPERSONATE_AS)
    classroom_service = build("classroom", "v1", credentials=classroom_creds)

    df = read_sheet(build, sheet_id, "n8n_student", sheet_creds)

    if df.empty:
        logging.warning("No student data returned nothing to invite")
        return

    if "payment_details" not in df.columns or "email" not in df.columns:
        logging.error(f"Expected columns missing. Got: {list(df.columns)}")
        sys.exit(1)

    invited_count = 0
    for _, row in df.iterrows():
        payment_status = str(row.get("payment_details", "")).strip().lower()
        email = row.get("email")

        if not email or not isinstance(email, str):
            logging.warning(f"Skipping row with missing/invalid email: {row.to_dict()}")
            continue

        if payment_status == "paid":
            invite_student(classroom_service, course_id, email, role="STUDENT")
            invited_count += 1

    logging.info(f"Done. Processed {invited_count} paid student(s).")


if __name__ == "__main__":
    main()