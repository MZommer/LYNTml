import inspect
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps

from core.logger import logger


@dataclass(slots=True)
class StructInfo:
    seed: int
    size_of: int


# Decorator
def lyn_struct(_func: Callable | None = None, *, trustable: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        signature = inspect.signature(func)
        accepts_struct = "struct" in signature.parameters or any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in signature.parameters.values()
        )

        @wraps(func)
        def wrapper(self: "TimelineSerializer", *args, **kwargs):
            seed = self._reader.tell()
            size_of = self._reader.uint32()  # Every struct is aligned
            struct = StructInfo(
                seed=seed,
                size_of=size_of,
            )
            if accepts_struct:
                kwargs["struct"] = struct
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
