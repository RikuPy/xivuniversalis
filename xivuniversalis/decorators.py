from functools import wraps

__all__ = ["supports_multiple_ids"]


def supports_multiple_ids(func):
    @wraps(func)
    async def wrapper(self, item_ids, *args, **kwargs):
        result = await func(self, item_ids, *args, **kwargs)
        if isinstance(item_ids, int):
            assert isinstance(result, dict)
            key = next(iter(result))
            return result[key]
        return result

    return wrapper
