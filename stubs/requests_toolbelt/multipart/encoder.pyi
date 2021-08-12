from typing import Any, Dict

class MultipartEncoder:
    boundary_value: Any
    boundary: Any
    encoding: Any
    fields: Any
    finished: bool
    parts: Any
    def __init__(self, fields: Dict[str, Any], boundary: Any | None = ..., encoding: str = ...) -> None: ...
    @property
    def len(self) -> int: ...
    @property
    def content_type(self) -> str: ...
    def to_string(self) -> bytes: ...
    def read(self, size: int = ...) -> bytes: ...
