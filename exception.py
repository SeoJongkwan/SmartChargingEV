class MessageTypeException(Exception):
    def __init__(
            self,
            message="Message Type must use predefined message type"
    ):
        self.message = message