import inflect

engine = inflect.engine()


def pluralize(word: str) -> str:
    return engine.plural(word)
