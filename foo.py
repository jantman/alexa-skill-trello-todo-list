# -*- coding: utf-8 -*-

# This is a Color Picker Alexa Skill.
# The skill serves as a simple sample on how to use
# session attributes.

import logging
import os

from trello import TrelloApi
import requests

logging.basicConfig(level=logging.DEBUG)
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

print(TrelloWrapper().text_for_lists())
