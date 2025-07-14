class BotError(Exception): pass
class CustomBotError(BotError): pass
class InvalidCallbackData(BotError): pass
class MissingMessage(BotError): pass
class MissingArgs(BotError): pass
class EmptyResourceList(BotError): pass
