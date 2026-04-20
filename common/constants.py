# Content types that should be excluded from permissions (e.g. when listing them in the API).
# They are either internal to Django or not relevant for features that are exposed to end-users.
CONTENT_TYPES_TO_EXCLUDE = {
    "admin": ["logentry"],
    "contenttypes": ["contenttype"],
    "sessions": ["session"],
    "token_blacklist": ["blacklistedtoken", "outstandingtoken"],
}
