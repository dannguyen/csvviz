class InvalidColorScheme(ValueError):
    pass


class InvalidDataReference(ValueError):
    def __init__(self, msg):
        super().__init__(f"InvalidDataReference: {msg}")
