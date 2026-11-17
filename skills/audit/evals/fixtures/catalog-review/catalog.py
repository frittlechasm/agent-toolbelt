CATALOG = {
    "notice_existing": {"body": "Hello {{subject}}", "required": "{{subject}}"},
}


def save(key, body):
    if key == "notice_existing" and "{{subject}}" not in body:
        raise ValueError("required field missing")
    CATALOG[key]["body"] = body
