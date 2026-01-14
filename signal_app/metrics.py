BRAND_TIER_ORDER = {
    "Global Ambassador": 1,
    "Ambassador": 2,
    "House Friend": 3,
    "Appearance": 4
}


def normalize_value(metric_key, value_num, value_text):
    if metric_key == "brand_tier" and value_text:
        return BRAND_TIER_ORDER.get(value_text, None), value_text
    return value_num, value_text
