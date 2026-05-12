"""
Auto-loaded by Python on startup (PEP 370 / sitecustomize).

Monkey-patches requests.Session to skip TLS verification ONLY when proxies are
configured on the session. Required because ScraperAPI's proxy mode does TLS
termination at their edge, presenting a certificate not signed by any public
CA — official ScraperAPI docs explicitly say to use verify=False.

Adapters that don't use proxies (arxiv, pubmed, biorxiv, medrxiv) keep full
TLS verification.
"""
try:
    import requests
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning

    urllib3.disable_warnings(InsecureRequestWarning)

    _orig_request = requests.Session.request

    def _request_skip_verify_when_proxied(self, method, url, **kwargs):
        if getattr(self, "proxies", None):
            kwargs.setdefault("verify", False)
        return _orig_request(self, method, url, **kwargs)

    requests.Session.request = _request_skip_verify_when_proxied
except Exception:
    pass
