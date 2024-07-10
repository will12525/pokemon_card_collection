import json
from unittest import TestCase
from bs4 import BeautifulSoup as bs
import re
from database_handler import input_file_parser, common_objects
from deck import read_file


class TestDBCreatorInit(TestCase):
    DATA_PATH = "../data_files/set_htmls/"

    def setUp(self) -> None:
        pass
        # self.media_directory_info = config_file_handler.load_json_file_content().get("media_folders")

        # __init__.patch_get_file_hash(self)
        # __init__.patch_get_ffmpeg_metadata(self)
        # __init__.patch_move_media_file(self)
        # __init__.patch_extract_subclip(self)
        # __init__.patch_update_processed_file(self)

    def load_set_data_count(self, count):
        set_data_list = []
        for set_data in input_file_parser.load_set_data_dir(self.DATA_PATH):
            set_data_list.append(set_data)
            if len(set_data_list) == count:
                break
        return set_data_list


class TestDBCreator(TestDBCreatorInit):
    #
    # def test_parse_set_codes(self):
    #     set_codes = input_file_parser.parse_set_codes()
    #     print(set_codes)
    #
    # # def test_setup_new_media_metadata(self):
    #
    # # with DBCreator(DBType.MEMORY) as db_setter_connection:
    # #     db_setter_connection.create_db()
    #
    # # if media_path_data := config_file_handler.load_json_file_content().get("media_folders"):
    # #     for media_path in media_path_data:
    # #         # print(media_path)
    # #         db_setter_connection.setup_media_directory(media_path)
    # def test_parse_set_data(self):
    #     set_codes = input_file_parser.parse_set_data()
    #     print(set_codes)

    def test_load_set_data(self):
        set_data_list = self.load_set_data_count(1)
        assert len(set_data_list) == 1
        for set_data in set_data_list:
            assert len(set_data) == 186
            for card_key, card_value in set_data.items():
                assert type(card_key) is tuple
                assert type(card_key[0]) is str
                assert type(card_key[1]) is str
                assert common_objects.STATE_HAVE_COLUMN in card_value
                assert type(card_value[common_objects.STATE_HAVE_COLUMN]) is int
                assert common_objects.STATE_WANT_COLUMN in card_value
                assert type(card_value[common_objects.STATE_WANT_COLUMN]) is int
                assert common_objects.CARD_NAME_COLUMN in card_value
                assert type(card_value[common_objects.CARD_NAME_COLUMN]) is str
                assert common_objects.SET_NAME_COLUMN in card_value
                assert type(card_value[common_objects.SET_NAME_COLUMN]) is str
                assert common_objects.PRICE_COLUMN in card_value
                assert type(card_value[common_objects.PRICE_COLUMN]) is float
                assert common_objects.CARD_RARITY_COLUMN in card_value
                assert common_objects.CARD_INDEX_COLUMN in card_value
                assert common_objects.STATE_GIFT_COLUMN in card_value
                assert common_objects.TCGP_ID_COLUMN in card_value
                assert type(card_value[common_objects.TCGP_ID_COLUMN]) is int
                assert common_objects.TCGP_PATH_COLUMN in card_value
                assert type(card_value[common_objects.TCGP_PATH_COLUMN]) is str

        # set_data = list(input_file_parser.load_set_data(self.DATA_PATH))
        # print(set_data)
