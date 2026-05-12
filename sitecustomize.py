"""
Auto-loaded by Python on startup (PEP 370 / sitecustomize).

Patch 1 — requests.Session: skip TLS verification ONLY when proxies are
configured on the session. Required because ScraperAPI's proxy mode does TLS
termination at their edge, presenting a certificate not signed by any public
CA — official ScraperAPI docs explicitly say to use verify=False.

Adapters that don't use proxies (arxiv, pubmed, biorxiv, medrxiv) keep full
TLS verification.

Patch 2 — xml.etree.ElementTree.fromstring: fall back to lxml recovery mode
on ParseError. NCBI eFetch (used by the pubmed adapter) occasionally returns
XML where <AbstractText> contains malformed inline HTML-ish tags that strict
ET cannot parse, producing "mismatched tag" errors. lxml in recover mode
salvages a usable tree.
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

try:
    from xml.etree import ElementTree as _ET

    _orig_ET_fromstring = _ET.fromstring

    def _et_fromstring_recover(content):
        try:
            return _orig_ET_fromstring(content)
        except _ET.ParseError:
            from lxml import etree as _lx
            parser = _lx.XMLParser(recover=True, encoding="utf-8")
            data = content.encode("utf-8") if isinstance(content, str) else content
            root = _lx.fromstring(data, parser=parser)
            return _orig_ET_fromstring(_lx.tostring(root))

    _ET.fromstring = _et_fromstring_recover
except Exception:
    pass
