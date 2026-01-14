import json
from sqlalchemy import delete
from signal_app.config import load_metrics_config, load_watchlist, load_rss_sources
from signal_app.db import get_engine, get_session, init_db, Person, Observation
from signal_app.metrics import normalize_value
from connectors.lastfm import fetch_artist_stats
from datetime import date
from sqlalchemy import and_
from connectors.rss_koreansales import parse_items
import requests
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd


def _normalize_key(value):
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _ensure_person(session, people_map, person_key, display_name):
    person = people_map.get(person_key)
    if person:
        return person

    person = Person(
        person_key=person_key,
        display_name=display_name,
        category="Unknown",
        country=None
    )
    session.add(person)
    session.commit()
    people_map[person_key] = person
    return person


def _seed_people(session, watchlist):
    existing = {p.person_key: p for p in session.query(Person).all()}
    for entry in watchlist:
        person_key = entry["person_key"]
        if person_key in existing:
            person = existing[person_key]
            person.display_name = entry["display_name"]
            person.category = entry.get("category")
            person.country = entry.get("country")
        else:
            session.add(
                Person(
                    person_key=person_key,
                    display_name=entry["display_name"],
                    category=entry.get("category"),
                    country=entry.get("country")
                )
            )
    session.commit()


def run_lastfm_ingest():
    engine = init_db(get_engine())
    session = get_session(engine)

    _, metrics = load_metrics_config()
    watchlist = load_watchlist()

    _seed_people(session, watchlist)

    metric_keys = ["lastfm_listeners", "lastfm_playcount"]
    metric_defs = {key: metrics[key] for key in metric_keys if key in metrics}

    if not metric_defs:
        session.close()
        return 0

    people_map = {p.person_key: p for p in session.query(Person).all()}
    rows_written = 0
    today = date.today()

    for person in watchlist:
        person_key = person["person_key"]
        display_name = person["display_name"]
        stats = fetch_artist_stats(display_name)
        if not stats:
            continue

        for key, value in {
            "lastfm_listeners": stats.get("listeners"),
            "lastfm_playcount": stats.get("playcount")
        }.items():
            if key not in metric_defs:
                continue

            metric = metric_defs[key]
            value_num, value_text = normalize_value(key, value, None)

            session.execute(
                delete(Observation).where(
                    and_(
                        Observation.person_id == people_map[person_key].id,
                        Observation.metric_key == key,
                        Observation.date == today
                    )
                )
            )

            observation = Observation(
                person_id=people_map[person_key].id,
                metric_key=key,
                pillar=metric["pillar"],
                source=metric["source"],
                date=today,
                value_num=value_num,
                value_text=value_text,
                unit=metric["unit"],
                raw_json=json.dumps({"lastfm": True})
            )
            session.add(observation)
            rows_written += 1

    session.commit()
    session.close()
    return rows_written


def _fetch_rss_items(url):
    try:
        response = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": "SignalIndexRSS/1.0"}
        )
        response.raise_for_status()
    except Exception as exc:
        return [], f"{type(exc).__name__}: {exc}"

    if url.endswith(".csv"):
        try:
            df = pd.read_csv(StringIO(response.text))
        except Exception as exc:
            return [], f"{type(exc).__name__}: {exc}"

        items = []
        for _, row in df.iterrows():
            items.append({
                "title": row.get("Title", "") or "",
                "description": row.get("Description", "") or "",
                "pubDate": row.get("Date", "") or ""
            })
        return items, None

    soup = BeautifulSoup(response.text, "xml")
    items = []
    for item in soup.find_all("item"):
        items.append({
            "title": item.title.get_text(strip=True) if item.title else "",
            "description": item.description.get_text() if item.description else "",
            "pubDate": item.pubDate.get_text(strip=True) if item.pubDate else ""
        })
    return items, None


def run_rss_ingest():
    engine = init_db(get_engine())
    session = get_session(engine)

    _, metrics = load_metrics_config()
    sources = load_rss_sources()
    watchlist = load_watchlist()

    _seed_people(session, watchlist)

    people_map = {p.person_key: p for p in session.query(Person).all()}
    person_lookup = {}
    for person in watchlist:
        display_name = person["display_name"]
        person_key = person["person_key"]
        person_lookup[_normalize_key(display_name)] = person_key
        person_lookup[_normalize_key(person_key)] = person_key

    observations = {}
    items_total = 0
    parsed_total = 0
    errors = []
    sample_titles = []

    for source in sources:
        url = source["url"]
        items, error = _fetch_rss_items(url)
        if error:
            errors.append({"source": source.get("label", url), "error": error})
            continue

        items_total += len(items)
        parsed = parse_items(items)
        parsed_total += len(parsed)
        sample_titles.extend([item["title"] for item in items[:3]])
        for entry in parsed:
            metric_key = entry["metric_key"]
            if metric_key not in metrics:
                continue

            normalized_tag = _normalize_key(entry["tag"])
            person_key = person_lookup.get(normalized_tag, normalized_tag)
            person = _ensure_person(session, people_map, person_key, entry["tag"])

            metric = metrics[metric_key]
            key = (person.id, metric_key, entry["date"])
            value_num = entry["value_num"]
            if key in observations:
                current = observations[key]["value_num"]
                if metric["directionality"] == "lower_is_better":
                    value_num = min(current, value_num)
                else:
                    value_num = max(current, value_num)

            observations[key] = {
                "person_id": person.id,
                "metric_key": metric_key,
                "pillar": metric["pillar"],
                "source": metric["source"],
                "date": entry["date"],
                "value_num": value_num,
                "unit": metric["unit"]
            }

    rows_written = 0
    for (_, metric_key, date_value), data in observations.items():
        session.execute(
            delete(Observation).where(
                and_(
                    Observation.person_id == data["person_id"],
                    Observation.metric_key == metric_key,
                    Observation.date == date_value
                )
            )
        )
        observation = Observation(
            person_id=data["person_id"],
            metric_key=metric_key,
            pillar=data["pillar"],
            source=data["source"],
            date=data["date"],
            value_num=data["value_num"],
            value_text=None,
            unit=data["unit"],
            raw_json=json.dumps({"rss": True})
        )
        session.add(observation)
        rows_written += 1

    session.commit()
    session.close()
    return {
        "items": items_total,
        "parsed": parsed_total,
        "observations": rows_written,
        "errors": errors,
        "sample_titles": sample_titles[:10]
    }
