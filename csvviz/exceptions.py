class VizValueError(ValueError):
    pass


class InvalidColorScheme(VizValueError):
    pass


class InvalidDataReference(VizValueError):
    def __init__(self, msg):
        super().__init__(f"InvalidDataReference: {msg}")


class ConflictingArgs(VizValueError):
    def __init__(self, msg):
        super().__init__(f"ConflictingArgs: {msg}")
