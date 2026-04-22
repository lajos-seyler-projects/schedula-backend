from .default_column_preferences import DEFAULT_COLUMN_PREFERENCES


def get_preferences_for_table(table_id):
    return [
        {"table_id": table_id, **col}
        for col in DEFAULT_COLUMN_PREFERENCES.get(table_id, [])
    ]
