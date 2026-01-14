import yaml


def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_metrics_config(path="metrics.yml"):
    data = _load_yaml(path)
    return data.get("pillars", {}), data.get("metrics", {})


def load_watchlist(path="watchlist.yml"):
    data = _load_yaml(path)
    return data.get("people", [])


def load_templates(path="content_templates.yml"):
    data = _load_yaml(path)
    return data.get("templates", [])


def load_rss_sources(path="rss_sources.yml"):
    data = _load_yaml(path)
    return data.get("sources", [])
