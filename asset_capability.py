"""Per-asset capability descriptors for the SAP Datasphere Consumption API.

1.6.0 established that API capability varies **per asset, not per tenant**, and
that it is discoverable in two quite different ways:

============  ==========================================  =====================
Path          Discovered by                               Confirmed instance
============  ==========================================  =====================
declarative   reading ``$metadata`` before the request    analytical entities
                                                          declare
                                                          ``@Capabilities.CountRestrictions/Countable: false``
empirical     making the request and reading the failure  lineage-gated filters
                                                          -- nothing in
                                                          ``$metadata`` says an
                                                          asset has federated
                                                          sources
============  ==========================================  =====================

A layer that only parsed annotations would miss lineage entirely; one that only
learned from failures would burn a round trip discovering what ``$metadata``
gives away for free. So both paths write into the same descriptor.

Deliberately minimal for this release: two consumers, no speculative fields, no
tenant-wide pre-warming sweep. Descriptors live in the internal
``CacheManager`` -- *not* the protocol cache, whose ``cacheScope`` is a
two-valued literal about proxy-cacheability and cannot hold anything like this.
"""

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

from cache_manager import CacheCategory

#: Descriptors are stable -- an asset's lineage and countability change only
#: when someone remodels it -- so they tolerate a long TTL.
CAPABILITY_TTL_SECONDS = 3600

#: Reuse an existing long-lived category rather than inventing one; this keeps
#: the descriptor inside the cache's normal accounting and invalidation.
CAPABILITY_CATEGORY = CacheCategory.TABLE_SCHEMA

UNKNOWN = "unknown"
FILTER_FULL = "full"
FILTER_LINEAGE_LIMITED = "lineage_limited"


@dataclass
class AssetCapability:
    """What the API will accept for one asset.

    ``None`` means "not yet discovered" and is distinct from a discovered
    ``False`` -- the difference decides whether we may skip a probe.
    """

    space_id: str
    asset_id: str
    countable: Optional[bool] = None
    filter_profile: str = UNKNOWN
    source: Dict[str, str] = field(default_factory=dict)
    discovered_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _key(space_id: str, asset_id: str) -> str:
    return f"capability:{space_id}/{asset_id}"


def get(cache, space_id: str, asset_id: str) -> AssetCapability:
    """Return the cached descriptor, or a blank one if nothing is known yet."""
    cached = None
    try:
        cached = cache.get(_key(space_id, asset_id), CAPABILITY_CATEGORY)
    except Exception:
        cached = None
    if isinstance(cached, AssetCapability):
        return cached
    return AssetCapability(space_id=space_id, asset_id=asset_id)


def _store(cache, cap: AssetCapability) -> AssetCapability:
    try:
        cache.set(_key(cap.space_id, cap.asset_id), cap,
                  CAPABILITY_CATEGORY, ttl=CAPABILITY_TTL_SECONDS)
    except Exception:
        pass  # the cache is an optimisation; never fail a call over it
    return cap


def record_countable(cache, space_id: str, asset_id: str, countable: bool,
                     source: str = "declarative") -> AssetCapability:
    cap = get(cache, space_id, asset_id)
    cap.countable = countable
    cap.source["countable"] = source
    cap.discovered_at = time.time()
    return _store(cache, cap)


def record_filter_profile(cache, space_id: str, asset_id: str, profile: str,
                          source: str = "empirical") -> AssetCapability:
    """Remember whether an asset accepts the full filter grammar.

    Called after a request has already told us -- lineage gating is only
    observable as a failure, so this is memoisation of a verdict, not a
    prediction.
    """
    cap = get(cache, space_id, asset_id)
    cap.filter_profile = profile
    cap.source["filter_profile"] = source
    cap.discovered_at = time.time()
    return _store(cache, cap)


def is_lineage_limited(cache, space_id: str, asset_id: str) -> bool:
    """True only if we have *already learned* this asset is lineage-limited."""
    return get(cache, space_id, asset_id).filter_profile == FILTER_LINEAGE_LIMITED


def consume_lineage_verdict(cache, space_id: str, asset_id: str) -> bool:
    """Check the remembered verdict **and clear it**, so it deflects once.

    This is what makes the memo safe to act on. The verdict is inferred from a
    failure, and inference can be wrong -- an unrelated error could in
    principle mark a healthy asset. If acting on it merely blocked the request
    for the life of the cache entry, a bad inference would cost an hour of
    working filters.

    Clearing on read caps that at exactly one deflected call: the caller gets
    the actionable message immediately instead of waiting for a round trip
    that would have failed, and if the verdict was wrong the very next attempt
    goes to the wire and succeeds. A genuinely lineage-limited asset simply
    re-records on its next failure.
    """
    cap = get(cache, space_id, asset_id)
    if cap.filter_profile != FILTER_LINEAGE_LIMITED:
        return False
    cap.filter_profile = UNKNOWN
    cap.source.pop("filter_profile", None)
    _store(cache, cap)
    return True


def countability_from_metadata(xml_content: str) -> Optional[bool]:
    """Read ``Capabilities.CountRestrictions/Countable`` out of ``$metadata``.

    Returns ``None`` when the annotation is absent, which is the common case:
    relational assets in an 80-asset scan declared no ``CountRestrictions`` at
    all, and absence means countable.

    Parsed textually rather than via ElementTree because the annotation sits in
    a ``<Record>`` under an external ``<Annotations Target=...>`` block, and the
    surrounding structure varies between the relational and analytical shapes.
    """
    if not xml_content or "CountRestrictions" not in xml_content:
        return None
    window_start = xml_content.find("CountRestrictions")
    window = xml_content[window_start:window_start + 400]
    if 'Property="Countable"' not in window:
        return None
    marker = window.find('Property="Countable"')
    tail = window[marker:marker + 120]
    if 'Bool="false"' in tail:
        return False
    if 'Bool="true"' in tail:
        return True
    return None
