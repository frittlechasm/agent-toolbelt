from catalog import CATALOG


GROUP_PREFIXES = {"Messages": ("notice_",)}


def visible_keys():
    return [key for key in CATALOG if any(key.startswith(prefix) for prefixes in GROUP_PREFIXES.values() for prefix in prefixes)]
