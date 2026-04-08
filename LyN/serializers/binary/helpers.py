from collections.abc import Callable
from functools import wraps

from core.logger import logger


# Decorator
def lyn_struct(_func: Callable | None = None, *, trustable: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            struct = self._reader.init_struct()
            try:
                ret = func(self, *args, **kwargs)
            except Exception:
                logger.exception(f"Error in {func.__name__}")
                ret = None
            finally:
                current = self._reader.tell()
                end_expected = struct.seed + struct.size_of
                if current < end_expected:
                    logger.debug(
                        f"[{func.__name__}] Struct ended early:"
                        f" {current} < {end_expected}"
                    )
                if current > end_expected + (8 if trustable else 0):
                    logger.debug(
                        f"[{func.__name__}] Struct overread: {current} > {end_expected}"
                    )
                self._reader.seek(end_expected)
            return ret

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
