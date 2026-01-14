import json
from sqlalchemy import delete
from app.config import load_metrics_config, load_watchlist
from app.db import get_engine, get_session, init_db, Person, Observation
from app.metrics import normalize_value
from connectors.lastfm import fetch_artist_stats
from datetime import date
from sqlalchemy import and_


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
