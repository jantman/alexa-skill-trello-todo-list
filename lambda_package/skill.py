# -*- coding: utf-8 -*-

# This is a Color Picker Alexa Skill.
# The skill serves as a simple sample on how to use
# session attributes.

import logging
import os

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor
)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

from trello import TrelloApi
import requests


skill_name = "Trello"
help_text = ("You can ask me to read your current to do list by asking "
             "what's on my list, or you can add an item by telling me to add "
             "foo to my list.")

todo_slot_key = "TODO"
todo_slot = 'ToDoItem'

sb = SkillBuilder()

logger = logging.getLogger(__name__)
if 'DEBUG' in os.environ:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class TrelloWrapper(object):

    board_get_kwargs = {
        'cards': 'visible',
        'card_fields': 'all',
        'lists': 'all',
        'list_fields': 'all'
    }

    def __init__(self):
        logger.debug('Initializing TrelloApi')
        self._trello = TrelloApi(
            os.environ['TRELLO_APP_KEY'], os.environ['TRELLO_TOKEN']
        )
        self._board_id = os.environ['TRELLO_BOARD_ID']
        self._board = self._trello.boards.get(
            self._board_id, **self.board_get_kwargs
        )
        self._add_list_id = os.environ['TRELLO_ADD_LIST_ID']
        self._read_list_ids = os.environ['TRELLO_READ_LIST_IDS'].split(',')

    def text_for_lists(self):
        lists_id_to_name = {}
        res = ''
        for l in self._board['lists']:
            if l['closed']:
                continue
            lists_id_to_name[l['id']] = l['name']
        for lid in self._read_list_ids:
            card_titles = self._text_for_list(lid)
            if len(card_titles) == 0:
                res += 'List %s is empty. ' % lists_id_to_name[lid]
                continue
            res += 'List %s has %d cards: %s. ' % (
                lists_id_to_name[lid], len(card_titles), ', '.join(card_titles)
            )
        return res

    def _text_for_list(self, list_id):
        cards = self.filter_cards(self._board['cards'], list_id)
        return [
            c['name'] for c in sorted(cards, key=lambda x: x['pos'])
        ]

    def add_card(self, title):
        self._new_card(
            name=title, idList=self._add_list_id,
            desc='added by Alexa trello skill',
            pos='top'
        )
        return 'New card, %s, has been added to trello.' % title

    def _new_card(self, **kwargs):
        """
        Wrapper around trello.cards.new because 0.9.1 on PyPI doesn't have a
        position argument (even though the source repo does...)

        :param name: card title
        :type name: str
        :param idList: list ID
        :type idList: str
        :param desc: card description
        :type desc: str
        :param pos: position, "top", "bottom", or a positive number
        """
        c = self._trello.cards
        resp = requests.post(
            "https://trello.com/1/cards" % (),
            params=dict(key=c._apikey, token=c._token),
            data=kwargs)
        resp.raise_for_status()
        return resp.json()

    def filter_cards(self, orig_cards, list_id):
        """filter cards to ones with a due date, and if list_id is not None,
        also in the specified list"""
        cards = []
        logger.debug('Filtering %d cards on board', len(orig_cards))
        for card in orig_cards:
            if list_id is not None and list_id != card['idList']:
                logger.debug('Skipping card %s (%s) in wrong list (%s)',
                             card['id'], card['name'], card['idList'])
                continue
            cards.append(card)
        logger.info('Identified %d cards in list', len(cards))
        return cards


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
        speech_text =TrelloWrapper().text_for_lists()

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
            speech = TrelloWrapper().add_card(item)
            handler_input.response_builder.speak(
                speech
            ).set_should_end_session(True)
            return handler_input.response_builder.response
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
        logger.debug('Alexa Response: %s', response)


class SkillRequestInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug(
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
