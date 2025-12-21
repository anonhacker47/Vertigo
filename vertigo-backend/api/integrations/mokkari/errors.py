class MokkariUnavailable:
    """
    Small marker class (not an Exception) used to return structured error info.
    We return dicts to keep routes simple and APIFairy-compatible.
    """
    def __init__(self, message: str):
        self.message = message

    def to_response(self):
        return {"items": [], "error": self.message}
