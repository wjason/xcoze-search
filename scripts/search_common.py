"""Shared provider contracts; standard library only."""
import ipaddress
import re
import urllib.parse


class SearchError(Exception):
    def __init__(self, code, message, *, status=None, retryable=False, category=None):
        super().__init__(message)
        self.code, self.status, self.retryable = code, status, retryable
        self.attempts = 0
        self.category = category or (
            "authentication" if status in (401, 403) or code.startswith("UnauthorizedOperation") else
            "billing" if status == 402 or code.startswith("ResourceUnavailable") else
            "billing" if status in (432, 433) else
            "rate_limit" if status == 429 or code.startswith("RequestLimitExceeded") else
            "budget" if code == "budget_exhausted" else
            "credentials" if code in ("missing_api_key", "invalid_key") else
            "response" if code in ("invalid_response", "response_too_large", "extraction_failed") else
            "configuration" if "config" in code else
            "input" if status in (400, 422) or code in ("invalid_input", "unsupported_option", "unsupported_operation") else
            "network" if code in ("network_error", "retry_later") else "provider")

    def data(self):
        return {"code": self.code, "message": str(self), "http_status": self.status,
                "category": self.category, "retryable": self.retryable, "attempts": self.attempts}


def invalid(message):
    raise SearchError("invalid_input", message)


def public_url(url):
    try:
        parsed = urllib.parse.urlsplit(url)
        if (len(url) > 8192 or parsed.scheme not in ("https", "http") or not parsed.hostname
                or parsed.username is not None or parsed.password is not None
                or any(c.isspace() or ord(c) < 32 for c in url)):
            return False
        parsed.port
        host = parsed.hostname.lower().rstrip(".")
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return "." in host
    except (ValueError, TypeError):
        return False


def text_field(item, name, *, optional=False):
    value = item.get(name)
    if value is None and optional:
        return ""
    if not isinstance(value, str):
        raise SearchError("invalid_response", "Invalid provider text field: " + name)
    return value


def text_list(item, name):
    value = item.get(name) or []
    if not isinstance(value, list) or any(not isinstance(part, str) for part in value):
        raise SearchError("invalid_response", "Invalid provider text array: " + name)
    return value


def validate_site(site):
    if site and (len(site) > 253 or not re.fullmatch(
            r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,63}", site)):
        invalid("--site requires one public domain, e.g. example.com (use punycode for IDNs).")


class RequestBudget:
    """Count actual HTTP attempts, including failed requests and retries."""
    def __init__(self, limit):
        if type(limit) is not int or not 1 <= limit <= 1000:
            invalid("Request budget must be 1..1000.")
        self.limit, self.used, self.by_provider = limit, 0, {}

    def consume(self, provider):
        if self.used >= self.limit:
            raise SearchError("budget_exhausted", "HTTP attempt budget exhausted; no further requests sent.")
        self.used += 1
        self.by_provider[provider] = self.by_provider.get(provider, 0) + 1

    def data(self):
        return {"limit": self.limit, "attempts": self.used, "remaining": self.limit - self.used,
                "by_provider": dict(self.by_provider), "scope": "current_invocation", "unit": "provider_api_http_attempts"}
