def snake_to_camel(name: str, overrides: dict[str, str] | None = None) -> str:
    """
    Converts name from snake case to camel case. If name is in overrides, then return
    the overridden value instead.

    Examples:

    assert snake_to_camel("foo_bar_baz") == "fooBarBaz"
    assert snake_to_camel("foo_bar_baz", {"foo_bar_baz": "fooBARBaz}) == "fooBARBaz"
    """
    if overrides is not None and name in overrides:
        return overrides[name]

    words = [word.title() for word in name.split("_")]
    words[0] = words[0].lower()
    return "".join(words)
