class VizValueError(ValueError):
    pass


class InvalidColorScheme(VizValueError):
    pass


class InvalidDataReference(VizValueError):
    def __init__(self, msg):
        super().__init__(f"InvalidDataReference: {msg}")


class MissingDataReference(VizValueError):
    def __init__(self, msg):
        super().__init__(f"MissingDataReference: {msg}")
