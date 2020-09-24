class InvalidColorScheme(ValueError):
    pass


class InvalidColumnName(ValueError):
    def __init__(self, msg):
        super().__init__(f"InvalidColumnName: {msg}")
