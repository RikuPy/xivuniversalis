from functools import wraps


def supports_multiple_ids(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if len(result) == 1:
            return result[0]
        return result

    return wrapper