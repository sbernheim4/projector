from __future__ import annotations


def pascal_case(name: str) -> str:
    parts: list[str] = []
    token = []

    for char in name:
        if char in {"_", "-", " "}:
            if token:
                parts.append("".join(token))
                token = []
            continue
        if char.isupper() and token:
            parts.append("".join(token))
            token = [char.lower()]
            continue
        token.append(char.lower() if not token else char)

    if token:
        parts.append("".join(token))

    return "".join(part[:1].upper() + part[1:] for part in parts if part)
