import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup


DATE_IN_TITLE_RE = re.compile(r"\\((\\d{2})\\.(\\d{2})\\.(\\d{2})\\)")
HASHTAG_LINE_RE = re.compile(r"#([A-Za-z0-9_]+).*?(\\d[\\d,]*)\\s+copies", re.IGNORECASE)
TOTAL_RE = re.compile(r"TOTAL\\s*[:\\-]\\s*([\\d,]+)", re.IGNORECASE)
NUMBER_RE = re.compile(r"(\\d[\\d,]*)")


def _parse_date_from_title(title):
    match = DATE_IN_TITLE_RE.search(title or "")
    if not match:
        return None
    year, month, day = [int(part) for part in match.groups()]
    year += 2000
    return datetime(year, month, day).date()


def _parse_pub_date(pub_date):
    if not pub_date:
        return None
    try:
        return parsedate_to_datetime(pub_date).date()
    except Exception:
        try:
            return datetime.fromisoformat(pub_date.replace("Z", "+00:00")).date()
        except Exception:
            return None


def _extract_text(html_text):
    if not html_text:
        return ""
    return BeautifulSoup(html_text, "lxml").get_text(separator="\\n")


def parse_items(items):
    observations = []

    for item in items:
        title = item.get("title", "")
        description = _extract_text(item.get("description", ""))
        pub_date = _parse_pub_date(item.get("pubDate"))

        if "Hanteo Album Chart" in title and "Daily" in title:
            chart_date = _parse_date_from_title(title) or pub_date
            observations.extend(
                _parse_hanteo_daily_chart(description, chart_date)
            )
            continue

        if "1st Week Sales" in title or "1st Week Sales" in description:
            observations.extend(
                _parse_hanteo_first_week(description, pub_date)
            )

    return observations


def _parse_hanteo_daily_chart(text, date_value):
    if not date_value:
        return []
    results = []
    for line in text.splitlines():
        match = HASHTAG_LINE_RE.search(line)
        if not match:
            continue
        tag, copies = match.groups()
        value = int(copies.replace(",", ""))
        results.append({
            "tag": tag,
            "metric_key": "realtime_pos_sales",
            "date": date_value,
            "value_num": value
        })
    return results


def _parse_hanteo_first_week(text, date_value):
    if not date_value:
        return []
    tag_match = re.search(r"#([A-Za-z0-9_]+)", text)
    if not tag_match:
        return []

    total_match = TOTAL_RE.search(text)
    if total_match:
        value = int(total_match.group(1).replace(",", ""))
    else:
        numbers = [int(val.replace(",", "")) for val in NUMBER_RE.findall(text)]
        value = max(numbers) if numbers else None

    if value is None:
        return []

    return [{
        "tag": tag_match.group(1),
        "metric_key": "chodong_first_week",
        "date": date_value,
        "value_num": value
    }]
