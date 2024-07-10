from unittest import TestCase
import database_handler.common_objects as co


class TestCardInfo(TestCase):
    def test_constructor(self):
        card_info = co.CardInfo()
        print(vars(card_info))

    def test_get_set_index(self):
        print(co.get_set_index("Base set"))
