"""
Cache Manager for SAP Datasphere MCP Server

Implements intelligent caching for frequently accessed data to improve performance
and reduce redundant API calls. Uses TTL-based expiration and LRU eviction.
"""

import time
import logging
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CacheCategory(Enum):
    """Categories of cached data with different TTL settings"""
    SPACES = "spaces"              # Space listings (TTL: 5 minutes)
    SPACE_INFO = "space_info"      # Individual space details (TTL: 5 minutes)
    TABLE_SCHEMA = "table_schema"  # Table schemas (TTL: 30 minutes)
    CONNECTIONS = "connections"    # Connection status (TTL: 1 minute)
    TASKS = "tasks"                # Task status (TTL: 30 seconds)
    MARKETPLACE = "marketplace"    # Marketplace packages (TTL: 1 hour)


@dataclass
class CacheEntry:
    """Represents a single cache entry"""
    key: str
    value: Any
    category: CacheCategory
    created_at: float
    ttl_seconds: int
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """Check if cache entry has exceeded its TTL"""
        return (time.time() - self.created_at) > self.ttl_seconds

    def is_valid(self) -> bool:
        """Check if cache entry is still valid"""
        return not self.is_expired()

    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = time.time()
        self.access_count += 1


class CacheManager:
    """
    Intelligent cache manager with TTL and LRU eviction

    Features:
    - Category-based TTL (different expiration times for different data types)
    - LRU eviction when max size reached
    - Cache statistics and monitoring
    - Manual invalidation support
    """

    # Default TTL values per category (in seconds)
    DEFAULT_TTL = {
        CacheCategory.SPACES: 300,         # 5 minutes
        CacheCategory.SPACE_INFO: 300,     # 5 minutes
        CacheCategory.TABLE_SCHEMA: 1800,  # 30 minutes
        CacheCategory.CONNECTIONS: 60,     # 1 minute
        CacheCategory.TASKS: 30,           # 30 seconds
        CacheCategory.MARKETPLACE: 3600,   # 1 hour
    }

    def __init__(self, max_size: int = 1000, enabled: bool = True):
        """
        Initialize cache manager

        Args:
            max_size: Maximum number of entries to cache
            enabled: Whether caching is enabled
        """
        self.max_size = max_size
        self.enabled = enabled
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
            "total_requests": 0
        }
        logger.info(f"Cache manager initialized (max_size={max_size}, enabled={enabled})")

    def get(self, key: str, category: CacheCategory) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key
            category: Category of cached data

        Returns:
            Cached value if found and valid, None otherwise
        """
        self._stats["total_requests"] += 1

        if not self.enabled:
            return None

        cache_key = self._make_cache_key(key, category)

        if cache_key in self._cache:
            entry = self._cache[cache_key]

            # Check if expired
            if entry.is_expired():
                logger.debug(f"Cache expired: {cache_key}")
                del self._cache[cache_key]
                self._stats["misses"] += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(cache_key)
            entry.touch()
            self._stats["hits"] += 1

            logger.debug(f"Cache hit: {cache_key} (age: {time.time() - entry.created_at:.1f}s)")
            return entry.value

        self._stats["misses"] += 1
        logger.debug(f"Cache miss: {cache_key}")
        return None

    def set(self, key: str, value: Any, category: CacheCategory, ttl: Optional[int] = None):
        """
        Store value in cache

        Args:
            key: Cache key
            value: Value to cache
            category: Category of data
            ttl: Optional custom TTL in seconds (overrides default)
        """
        if not self.enabled:
            return

        cache_key = self._make_cache_key(key, category)
        ttl_seconds = ttl if ttl is not None else self.DEFAULT_TTL[category]

        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            value=value,
            category=category,
            created_at=time.time(),
            ttl_seconds=ttl_seconds,
            access_count=0,
            last_accessed=time.time()
        )

        # Evict if at max size
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        self._cache[cache_key] = entry
        self._cache.move_to_end(cache_key)

        logger.debug(f"Cache set: {cache_key} (TTL: {ttl_seconds}s)")

    def invalidate(self, key: str, category: CacheCategory):
        """
        Invalidate a specific cache entry

        Args:
            key: Cache key to invalidate
            category: Category of data
        """
        if not self.enabled:
            return

        cache_key = self._make_cache_key(key, category)

        if cache_key in self._cache:
            del self._cache[cache_key]
            self._stats["invalidations"] += 1
            logger.info(f"Cache invalidated: {cache_key}")

    def invalidate_category(self, category: CacheCategory):
        """
        Invalidate all entries of a specific category

        Args:
            category: Category to invalidate
        """
        if not self.enabled:
            return

        keys_to_remove = [
            key for key, entry in self._cache.items()
            if entry.category == category
        ]

        for key in keys_to_remove:
            del self._cache[key]
            self._stats["invalidations"] += 1

        logger.info(f"Cache category invalidated: {category.value} ({len(keys_to_remove)} entries)")

    def invalidate_all(self):
        """Clear entire cache"""
        if not self.enabled:
            return

        count = len(self._cache)
        self._cache.clear()
        self._stats["invalidations"] += count
        logger.info(f"Cache cleared: {count} entries removed")

    def cleanup_expired(self):
        """Remove all expired entries from cache"""
        if not self.enabled:
            return

        keys_to_remove = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]

        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            logger.info(f"Cache cleanup: {len(keys_to_remove)} expired entries removed")

    def _evict_lru(self):
        """Evict least recently used entry"""
        if self._cache:
            evicted_key, evicted_entry = self._cache.popitem(last=False)
            self._stats["evictions"] += 1
            logger.debug(f"Cache eviction (LRU): {evicted_key}")

    def _make_cache_key(self, key: str, category: CacheCategory) -> str:
        """Create cache key with category prefix"""
        return f"{category.value}:{key}"

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["total_requests"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "enabled": self.enabled,
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate_percent": round(hit_rate, 2),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "invalidations": self._stats["invalidations"],
            "total_requests": self._stats["total_requests"]
        }

    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        category_counts = {}
        for entry in self._cache.values():
            cat = entry.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        entries_info = []
        for key, entry in list(self._cache.items())[-10:]:  # Last 10 entries
            entries_info.append({
                "key": key,
                "category": entry.category.value,
                "age_seconds": round(time.time() - entry.created_at, 1),
                "ttl_seconds": entry.ttl_seconds,
                "access_count": entry.access_count,
                "valid": entry.is_valid()
            })

        return {
            "stats": self.get_stats(),
            "categories": category_counts,
            "recent_entries": entries_info
        }

    def enable(self):
        """Enable caching"""
        self.enabled = True
        logger.info("Cache enabled")

    def disable(self):
        """Disable caching"""
        self.enabled = False
        logger.info("Cache disabled")


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(max_size=1000, enabled=True)
    return _cache_manager


def cache_get(key: str, category: CacheCategory) -> Optional[Any]:
    """Convenience function to get from cache"""
    return get_cache_manager().get(key, category)


def cache_set(key: str, value: Any, category: CacheCategory, ttl: Optional[int] = None):
    """Convenience function to set cache value"""
    get_cache_manager().set(key, value, category, ttl)


def cache_invalidate(key: str, category: CacheCategory):
    """Convenience function to invalidate cache entry"""
    get_cache_manager().invalidate(key, category)


def cache_stats() -> Dict[str, Any]:
    """Convenience function to get cache statistics"""
    return get_cache_manager().get_stats()
