from urllib.parse import urlsplit


def _host(url: str) -> str:
    return (urlsplit(url.strip()).hostname or "").removeprefix("www.")


def site_key(url: str) -> str:
    """Normalize a site URL for duplicate checks: host without www, plus path.

    The path matters because several sites can share one host (the local demo serves every
    fictional company from one nginx).
    """
    return f"{_host(url)}{urlsplit(url.strip()).path.rstrip('/')}".lower()


def same_host(url: str, other: str) -> bool:
    return bool(_host(url)) and _host(url).lower() == _host(other).lower()
