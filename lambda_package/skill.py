# -*- coding: utf-8 -*-

# This is a Color Picker Alexa Skill.
# The skill serves as a simple sample on how to use
# session attributes.

import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor
)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard


skill_name = "Trello"
help_text = ("You can ask me to read your current to do list by asking "
             "what's on my list, or you can add an item by telling me to add "
             "foo to my list.")

todo_slot_key = "TODO"
todo_slot = 'ToDoItem'

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech = "Welcome to the Trello skill!"
        handler_input.response_builder.speak(
            speech + " " + help_text).ask(help_text)
        return handler_input.response_builder.response


class ListToDoIntentHandler(AbstractRequestHandler):
    """Handler for ListToDo Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("ListToDo")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "If I was real, I would list your To Do list items!"

        handler_input.response_builder.speak(
            speech_text
        ).set_should_end_session(True)
        return handler_input.response_builder.response


class AddToDoIntentHandler(AbstractRequestHandler):
    """Handler for AddToDo Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddToDo")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots

        if todo_slot in slots:
            item = slots[todo_slot].value
            logger.info('Add Item: %s', item)
            speech = ("If I was real, I would add {} to your Trello To Do "
                      "list. You can ask me to read your list by saying, "
                      "what's on my list ?".format(item))
            reprompt = ("You can ask me to read your list by saying, "
                        "what's on my list ?")
        else:
            speech = "I'm not sure what you wanted to add, please try again"
            reprompt = ("I'm not sure what you wanted to add. "
                        "You can tell me to add thing to your todo list by "
                        "saying, ask trello to add thing to my list.")

        handler_input.response_builder.speak(speech).ask(reprompt)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        handler_input.response_builder.speak(help_text).ask(help_text)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"
        return handler_input.response_builder.speak(speech_text).response


class FallbackIntentHandler(AbstractRequestHandler):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Trello skill can't help you with that.  "
            "You can ask me what's on your list!!")
        reprompt = "You can ask me what's on your list!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


class SkillResponseInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.info('Alexa Response: %s', response)


class SkillRequestInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.info(
            "Alexa Request: %s", handler_input.request_envelope.request
        )


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(ListToDoIntentHandler())
sb.add_request_handler(AddToDoIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_global_request_interceptor(SkillRequestInterceptor())
sb.add_global_response_interceptor(SkillResponseInterceptor())

handler = sb.lambda_handler()
