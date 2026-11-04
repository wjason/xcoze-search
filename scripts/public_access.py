"""Per-machine public API pacing. No credentials, query text or response cache."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time
import urllib.error

from search_common import SearchError

INTERVALS = {"wikipedia": 1, "stackexchange": 1, "arxiv": 3, "crossref": 1,
             "npm": 1, "crates": 1, "gitlab": 2, "europepmc": 1, "huggingface": 1, "exa-free": 1, "duckduckgo": 1, "browser": 0}
INTERVALS.update({"bilibili-trending": 2, "zhihu-trending": 2, "v2ex-trending": 2})
INTERVALS.update({"cns-scroll": 2, "cns-finance": 2, "bbc-world": 2, "govcn": 2,
                  "community-v2ex": 2, "community-python": 2, "community-rust": 2})


def pause_status(name):
    """Read a source pause without creating files or accessing the network."""
    path = cache_root() / (name + ".json")
    try:
        if not path.exists(): return None
        if path.stat().st_size > 65536: raise ValueError
        data = json.loads(path.read_text(encoding="utf-8"))
        deadline = data.get("not_before", 0)
        if not isinstance(deadline, (int, float)) or not math.isfinite(deadline): raise ValueError
        remaining = deadline - time.time()
        # Tiny pacing intervals are handled inside request_slot, not planner skipping.
        if remaining > 3:
            return {"code": "source_cooldown", "retry_after_seconds": math.ceil(remaining)}
    except (OSError, ValueError, TypeError, AttributeError):
        return {"code": "public_access_state_error", "retry_after_seconds": None}
    return None


def cache_root():
    base = os.environ.get("XDG_CACHE_HOME") or os.environ.get("LOCALAPPDATA")
    return (Path(base) if base else Path.home() / ".cache") / "xcoze-search" / "public-access"


def cooldown():
    return SearchError("source_cooldown", "Public source is cooling down or a duplicate request was suppressed; retry later or use another allowed source.", category="rate_limit")


class Slot:
    def __init__(self, path, state):
        self.path, self.state = path, state
        self.waited_seconds = 0

    def save(self):
        fd, temporary = tempfile.mkstemp(prefix=".state-", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(self.state, stream)
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)

    def defer(self, seconds):
        if isinstance(seconds, bool): return
        try: seconds = float(seconds)
        except (TypeError, ValueError):
            try:
                seconds = parsedate_to_datetime(seconds).timestamp() - time.time()
            except (TypeError, ValueError, OverflowError, AttributeError): return
        if not math.isfinite(seconds) or seconds < 0: return
        self.state["not_before"] = max(self.state.get("not_before", 0), time.time() + seconds)
        self.save()

    def observe(self, raw):
        self.defer(raw.get("backoff"))
        if raw.get("quota_remaining") == 0:
            now = datetime.now(timezone.utc)
            reset = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            self.defer((reset - now).total_seconds())


@contextmanager
def request_slot(name, url, *, max_wait=0):
    if name not in INTERVALS:
        yield None
        return
    handle = None
    try:
        root = cache_root(); root.mkdir(parents=True, exist_ok=True, mode=0o700)
        handle = (root / (name + ".lock")).open("a+b")
        if handle.seek(0, 2) == 0:
            handle.write(b"\0"); handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise SearchError("source_busy", "Another local process is using this public API; retry later or use another allowed source.", category="rate_limit") from None
        path = root / (name + ".json")
        state = {}
        if path.exists():
            if path.stat().st_size > 65536: raise ValueError
            state = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(state, dict): raise ValueError
        now = time.time()
        not_before = state.get("not_before", 0)
        if not isinstance(not_before, (int, float)) or not math.isfinite(not_before): raise ValueError
        hashes = state.get("duplicate_until", {})
        if not isinstance(hashes, dict) or any(not isinstance(k, str) or not isinstance(v, (int, float)) or not math.isfinite(v) for k, v in hashes.items()):
            raise ValueError
        digest = hashlib.sha256(url.encode()).hexdigest()
        delay = max(not_before, hashes.get(digest, 0)) - now
        waited = 0
        if 0 < delay <= max_wait:
            started = time.monotonic()
            time.sleep(delay)
            waited = time.monotonic() - started
            now = time.time()
        if now < not_before or now < hashes.get(digest, 0): raise cooldown()
        state = {"not_before": now + INTERVALS[name], "duplicate_until": {k: v for k, v in hashes.items() if v > now}}
        if name == "stackexchange": state["duplicate_until"][digest] = now + 60
        slot = Slot(path, state); slot.waited_seconds = waited; slot.save()
    except SearchError:
        if handle:
            handle.close()
        raise
    except (OSError, ValueError, TypeError):
        if handle: handle.close()
        raise SearchError("public_access_state_error", "Cannot safely use local public-source pacing state; inspect the xcoze-search cache directory.", category="configuration") from None
    try:
        yield slot
    except urllib.error.HTTPError as error:
        if (name.endswith("-trending") or name.startswith("community-")) and error.code in (401, 403, 412): slot.defer(900)
        if error.code in (429, 503):
            default = 900 if name == "exa-free" else 60
            slot.defer(error.headers.get("Retry-After", str(default)) if error.headers else default)
        raise
    except SearchError as error:
        if (name.endswith("-trending") or name.startswith("community-")) and error.status in (401, 403, 412): slot.defer(900)
        if error.status in (429, 503): slot.defer(900 if name == "exa-free" else 60)
        if name == "exa-free" and error.code == "source_rate_limited": slot.defer(900)
        if name == "duckduckgo" and error.code == "access_challenge": slot.defer(900)
        if name == "browser":
            if error.code in ("access_challenge", "browser_navigation_blocked"): slot.defer(900)
            elif error.code in ("browser_timeout", "browser_no_results", "browser_results_hidden", "browser_navigation_failed", "browser_failed", "browser_unavailable"): slot.defer(60)
        raise
    finally:
        # OS locks are released on close, including process exit; no stale lock deletion needed.
        handle.close()
