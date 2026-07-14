from googleapiclient.discovery import build
from src.invite import read_sheet, invite_student, cred, get_env

import logging

logging.basicConfig(level=logging.INFO, format= '%(astime)s - %(asmessage)s')
#============= Set up  environment variables ============
sheet_id = get_env("")
scope_sheet = get_env("")
class_scopes = get_env("")
analy_cred = get_env("analy_json")
de_nig = get_env("de_nig")
sheet_scope = get_env("")
#===============================================================

def main(key_path, course_id, analy_json, sheet_id, sheet_scope=sheet_scope):
    logging.info("Fetching Student information from sheet")
   

    sheet_scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    classroom_scope = ["https://www.googleapis.com/auth/classroom.rosters", "https://www.googleapis.com/auth/classroom.courses.readonly"]

    sheet_creds = cred(key_path, sheet_scope)

    classroom_creds = cred(analy_json, classroom_scope, subject="ezekiel.sanmabo@dedamdata.org")
    classroom_service = build("classroom", "v1", credentials=classroom_creds)

    df = read_sheet(sheet_id, 'nig_student', sheet_creds)

    for _, row in df.iterrows():          
        if row['payment_details'] == 'paid':   
            invite_student(classroom_service, course_id, row['email'], role='STUDENT')

if __name__ == "__main__":
    main()