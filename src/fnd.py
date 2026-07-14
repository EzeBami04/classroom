def find_course_id(service, name_contains: str):
    """
    List courses accessible to the authenticated user/service account,
    optionally filtering by name substring.
    """
    courses = []
    page_token = None

    while True:
        response = service.courses().list(
            pageToken=page_token,
            pageSize=50
        ).execute()

        courses.extend(response.get("courses", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    for c in courses:
        if not name_contains or name_contains.lower() in c["name"].lower():
            print(f"{c['name']} — {c['section']} — courseId: {c['id']}")

    return courses