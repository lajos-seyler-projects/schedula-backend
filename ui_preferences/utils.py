from .default_column_preferences import DEFAULT_COLUMN_PREFERENCES


def get_preferences_for_table(table_id):
    return [{"table_id": table_id, **col} for col in DEFAULT_COLUMN_PREFERENCES.get(table_id, [])]


def get_invalid_column_keys(table_id: str, requested_preferences: list[dict]) -> list[str]:
    """
    Returns keys from requested_preferences that don't exist in the defaults for the given table_id.
    """
    if not table_id or not requested_preferences:
        return None

    default_columns = DEFAULT_COLUMN_PREFERENCES.get(table_id, [])
    valid_keys = {col["key"] for col in default_columns}

    return [pref["key"] for pref in requested_preferences if pref["key"] not in valid_keys]
