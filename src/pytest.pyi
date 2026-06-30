from typing import Any, ContextManager


def raises(expected_exception: type[BaseException], *args: Any, **kwargs: Any) -> ContextManager[Any]: ...
