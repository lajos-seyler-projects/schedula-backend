from .constants import CONTENT_TYPES_TO_EXCLUDE


def get_excluded_content_types():
    excluded_content_types = []
    for app_label, models in CONTENT_TYPES_TO_EXCLUDE.items():
        for model in models:
            excluded_content_types.append(f"{app_label}.{model}")
    return excluded_content_types
