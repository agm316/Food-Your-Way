class pswdError(Exception):
    """
    Exception raised for invalid password depending
    on length, and content (to add later).

    Attributes:
        length -- the length that creates the error
        message -- explaining the error
    """

    def __init__(self, length, message="default"):

        if message != "default":
            self.message = message

        if length < 8:
            self.message = "Password too short, needs at least 8 characters"

        if length > 64:
            self.message = "Please limit pswd length to 64 chars"

        super().__init__(self.message)
