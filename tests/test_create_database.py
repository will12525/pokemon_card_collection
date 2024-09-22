import json
import os
from unittest import TestCase

# import config_file_handler
from database_handler import common_objects
from database_handler.db_getter import DatabaseHandler
from database_handler.db_setter import (
    DBCreator,
    sql_create_card_info_table,
    sql_insert_card_info_table,
)
from database_handler.input_file_parser import load_set_data_dir


class TestDBCreatorInit(TestCase):
    DB_PATH = "pokemon_card_data.db"
    DATA_PATH = "../data_files/set_htmls/"

    def setUp(self) -> None:
        pass
        # if os.path.exists(self.DB_PATH):
        #     os.remove(self.DB_PATH)
        # self.media_directory_info = config_file_handler.load_json_file_content().get("media_folders")

        # __init__.patch_get_file_hash(self)
        # __init__.patch_get_ffmpeg_metadata(self)
        # __init__.patch_move_media_file(self)
        # __init__.patch_extract_subclip(self)
        # __init__.patch_update_processed_file(self)

    def erase_db(self):
        if os.path.exists(self.DB_PATH):
            os.remove(self.DB_PATH)

    def populate_db(self, count):
        with DBCreator(common_objects.DBType.PHYSICAL) as db_setter_connection:
            db_setter_connection.create_db()
            index = 0
            for set_data in load_set_data_dir(self.DATA_PATH):
                db_setter_connection.add_set_card_data(set_data)
                index += 1
                if index == count:
                    break


class TestDBCreator(TestDBCreatorInit):

    def test_fill_database(self):
        # self.erase_db()
        with DBCreator(common_objects.DBType.PHYSICAL) as db_setter_connection:
            db_setter_connection.create_db()
            for set_data in load_set_data_dir(self.DATA_PATH):
                db_setter_connection.add_set_card_data(set_data)

    def test_custom_injection(self):
        card_machamp = {
            common_objects.STATE_HAVE_COLUMN: 0,
            common_objects.STATE_WANT_COLUMN: 0,
            common_objects.CARD_NAME_COLUMN: "Machamp",
            common_objects.SET_ID_COLUMN: 0,
            common_objects.PRICE_COLUMN: 6.0,
            common_objects.CARD_RARITY_COLUMN: "Unlimited Holofoil",
            common_objects.CARD_INDEX_COLUMN: 8,
            common_objects.STATE_GIFT_COLUMN: 0,
            common_objects.TCGP_ID_COLUMN: 107004,
            common_objects.TCGP_PATH_COLUMN: "deck-exclusives-machamp",
            common_objects.SET_NAME_COLUMN: "Base Set (Shadowless)",
            common_objects.SET_INDEX_COLUMN: 0,
        }
        card_treecko = {
            common_objects.STATE_HAVE_COLUMN: 0,
            common_objects.STATE_WANT_COLUMN: 0,
            common_objects.CARD_NAME_COLUMN: "Treecko Star",
            common_objects.SET_ID_COLUMN: 0,
            common_objects.PRICE_COLUMN: 500.0,
            common_objects.CARD_RARITY_COLUMN: "Holofoil",
            common_objects.CARD_INDEX_COLUMN: 109,
            common_objects.STATE_GIFT_COLUMN: 0,
            common_objects.TCGP_ID_COLUMN: 90046,
            common_objects.TCGP_PATH_COLUMN: "team-rocket-returns-treecko-star",
            common_objects.SET_NAME_COLUMN: "Team Rocket Returns",
            common_objects.SET_INDEX_COLUMN: 0,
        }
        card_vaporeon = {
            common_objects.STATE_HAVE_COLUMN: 0,
            common_objects.STATE_WANT_COLUMN: 0,
            common_objects.CARD_NAME_COLUMN: "Vaporeon Star",
            common_objects.SET_ID_COLUMN: 0,
            common_objects.PRICE_COLUMN: 450.0,
            common_objects.CARD_RARITY_COLUMN: "Holofoil",
            common_objects.CARD_INDEX_COLUMN: 102,
            common_objects.STATE_GIFT_COLUMN: 0,
            common_objects.TCGP_ID_COLUMN: 90292,
            common_objects.TCGP_PATH_COLUMN: "power-keepers-vaporeon-star",
            common_objects.SET_NAME_COLUMN: "Power Keepers",
            common_objects.SET_INDEX_COLUMN: 0,
        }
        with DBCreator(common_objects.DBType.PHYSICAL) as db_setter_connection:
            db_setter_connection.insert_card(card_machamp)
            db_setter_connection.insert_card(card_treecko)
            db_setter_connection.insert_card(card_vaporeon)

        with DatabaseHandler(common_objects.DBType.PHYSICAL) as db_getter_connection:
            print(db_getter_connection.get_card_from_id(card_machamp))
            print(db_getter_connection.get_card_from_id(card_treecko))
            print(db_getter_connection.get_card_from_id(card_vaporeon))

    def test_setup_new_media_metadata(self):
        self.erase_db()
        self.populate_db(1)
        with DatabaseHandler(common_objects.DBType.PHYSICAL) as db_getter_connection:
            card_data_list = db_getter_connection.get_all_card_data()
        assert type(card_data_list) is list
        print(len(card_data_list))
        assert len(card_data_list) == 186
        for card_data in card_data_list:
            print(card_data)
            assert type(card_data) is dict
            assert len(card_data) == 12

        # if media_path_data := config_file_handler.load_json_file_content().get("media_folders"):
        #     for media_path in media_path_data:
        #         # print(media_path)
        #         db_setter_connection.setup_media_directory(media_path)

    def test_get_all_sets(self):
        with DatabaseHandler(common_objects.DBType.PHYSICAL) as db_getter_connection:
            set_list = db_getter_connection.get_sets()
            print(set_list)

    def test_add_set_data(self):
        self.erase_db()
        base_set_set = {
            common_objects.ID_COLUMN: None,
            common_objects.SET_NAME_COLUMN: "Base set",
            common_objects.SET_INDEX_COLUMN: common_objects.get_set_index("Base set"),
        }
        aquapolis_set = {
            common_objects.ID_COLUMN: None,
            common_objects.SET_NAME_COLUMN: "Aquapolis",
            common_objects.SET_INDEX_COLUMN: common_objects.get_set_index("Aquapolis"),
        }
        with DBCreator(common_objects.DBType.PHYSICAL) as db_setter_connection:
            db_setter_connection.create_db()
            assert 1 == db_setter_connection.set_set_data(base_set_set)
            assert not db_setter_connection.set_set_data(base_set_set)
            assert 2 == db_setter_connection.set_set_data(aquapolis_set)
            print(
                db_setter_connection.get_set_id_from_name(
                    base_set_set.get(common_objects.SET_NAME_COLUMN)
                )
            )
            assert 1 == db_setter_connection.get_set_id_from_name(
                base_set_set.get(common_objects.SET_NAME_COLUMN, {})
            )
            assert 2 == db_setter_connection.get_set_id_from_name(
                aquapolis_set.get(common_objects.SET_NAME_COLUMN, {})
            )

        with DatabaseHandler(common_objects.DBType.PHYSICAL) as db_getter_connection:
            set_list = db_getter_connection.get_sets()
        print(set_list)
        assert len(set_list) == 2
        assert set_list[0].get(common_objects.SET_NAME_COLUMN) == base_set_set.get(
            common_objects.SET_NAME_COLUMN
        )
        assert set_list[1].get(common_objects.SET_NAME_COLUMN) == aquapolis_set.get(
            common_objects.SET_NAME_COLUMN
        )

    def test_multiple_set_names(self):
        expected_result = [
            {"id": 1, "set_name": "Aquapolis", common_objects.SET_INDEX_COLUMN: 14},
            {"id": 2, "set_name": "Arceus", common_objects.SET_INDEX_COLUMN: 42},
        ]
        self.erase_db()
        self.populate_db(2)
        with DatabaseHandler(common_objects.DBType.PHYSICAL) as db_getter_connection:
            set_list = db_getter_connection.get_sets()
        assert expected_result == set_list

    def test_table_constructors(self):
        # 0 == False
        # 1 == True
        print(sql_insert_card_info_table)
        print(sql_create_card_info_table)
