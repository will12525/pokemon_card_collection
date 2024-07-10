import json
import os
import sys
from unittest import TestCase

# import config_file_handler
from database_handler import common_objects as co, common_objects
from database_handler.db_getter import DatabaseHandler
from database_handler.db_setter import DBCreator

from database_handler.input_file_parser import (
    load_set_data_dir,
    load_set_data,
    download_tcgp_card_images,
)


# from database_handler.media_metadata_collector import get_playlist_list_index
# import database_handler.db_getter


class TestDBCreatorInit(TestCase):
    DB_PATH = "pokemon_card_data.db"
    DATA_PATH = "../data_files/set_htmls/"

    def setUp(self) -> None:
        pass
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
        with DBCreator(co.DBType.PHYSICAL) as db_setter_connection:
            db_setter_connection.create_db()
            index = 0
            for set_data in load_set_data_dir(self.DATA_PATH):
                db_setter_connection.add_set_card_data(set_data)
                index += 1
                if index == count:
                    break

    def populate_specific_set_data(self, set_path):
        with DBCreator(co.DBType.PHYSICAL) as db_setter_connection:
            db_setter_connection.create_db()
            db_setter_connection.add_set_card_data(
                load_set_data(f"{self.DATA_PATH}{set_path}.html")
            )


class TestDBCreator(TestDBCreatorInit):

    def test_count_alignment_on_read(self):
        file_path = f"{self.DATA_PATH}Arceus.html"
        set_data = load_set_data(file_path)
        # print(set_data)
        total_have = 0
        total_want = 0
        total_cards = 0
        cost_have = 0
        cost_want = 0
        cost_total = 0
        set_name = ""
        for key, item in set_data.items():
            # if item.get("state_want") == 0:
            #     continue
            print(item)
            total_cards += 1
            cost_total += item["price"]
            set_name = item["set_name"]
            if item["state_have"] >= 1:
                total_have += item["state_have"]
                cost_have += item["price"]
            if item["state_want"] >= 1:
                total_want += item["state_want"]
                cost_want += item["price"]
        print(f"Set name: {set_name}")
        print(
            f"total_have: {total_have}, total_want: {total_want}, total_cards: {total_cards}, "
        )
        print(
            f"cost_have: {cost_have}, cost_want: {cost_want}, cost_total: {cost_total}, "
        )

    def test_index_parsing(self):
        jungle_file_path = f"{self.DATA_PATH}Jungle.html"
        set_data = load_set_data(jungle_file_path)
        team_rocket_returns_file_path = f"{self.DATA_PATH}Team Rocket Returns.html"
        set_data = load_set_data(team_rocket_returns_file_path)

    def test_update_index(self):
        self.erase_db()
        self.populate_specific_set_data("Jungle")
        self.populate_specific_set_data("Base Set")
        self.populate_specific_set_data("Team Rocket Returns")
        # set_data = load_set_data(jungle_file_path)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            query_base_set = db_getter_connection.query_cards("Base Set (Shadowless)", "", "", "",
                                                              "").get("set_card_list")
            query_jungle = db_getter_connection.query_cards("Jungle", "", "", "", "").get(
                "set_card_list"
            )

        print(json.dumps(query_base_set[0], indent=4))
        assert query_base_set[0].get(common_objects.CARD_NAME_COLUMN) == "Alakazam"
        alakazam_card_id = query_base_set[0].get(common_objects.TCGP_ID_COLUMN)
        assert not query_base_set[0].get(common_objects.CARD_INDEX_COLUMN)

        print(json.dumps(query_jungle[17], indent=4))
        assert query_jungle[17].get(common_objects.CARD_NAME_COLUMN) == "Persian"
        persian_card_id = query_jungle[17].get(common_objects.TCGP_ID_COLUMN)
        assert not query_jungle[17].get(common_objects.CARD_INDEX_COLUMN)

        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            db_getter_connection.set_card_index(
                {
                    common_objects.TCGP_ID_COLUMN: alakazam_card_id,
                    common_objects.CARD_INDEX_COLUMN: 1,
                }
            )
            updated_query_base_set = db_getter_connection.query_cards("Base Set (Shadowless)", "", "", "",
                                                                      "").get("set_card_list")

            db_getter_connection.set_card_index(
                {
                    common_objects.TCGP_ID_COLUMN: persian_card_id,
                    common_objects.CARD_INDEX_COLUMN: 7,
                }
            )
            updated_query_jungle = db_getter_connection.query_cards("Jungle", "", "", "", "").get("set_card_list")

        alakazam_card_info = None
        for item in updated_query_base_set:
            if item.get(co.TCGP_ID_COLUMN) == alakazam_card_id:
                alakazam_card_info = item
                break
        print(json.dumps(alakazam_card_info, indent=4))
        assert alakazam_card_info.get(common_objects.CARD_INDEX_COLUMN) == 1

        persian_card_info = None
        for item in updated_query_jungle:
            if item.get(co.TCGP_ID_COLUMN) == persian_card_id:
                persian_card_info = item
                break
        print(json.dumps(persian_card_info, indent=4))
        assert persian_card_info.get(common_objects.CARD_INDEX_COLUMN) == 7

    def test_get_all_card_data(self):
        self.erase_db()
        self.populate_db(1)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            print(db_getter_connection.get_all_card_data())
            # db_setter_connection.create_db()
            # for set_data in load_set_data():
            #     for card in set_data.values():
            #         db_setter_connection.set_card_metadata(card)

            # if media_path_data := config_file_handler.load_json_file_content().get("media_folders"):
            #     for media_path in media_path_data:
            #         # print(media_path)
            #         db_setter_connection.setup_media_directory(media_path)

    def test_get_all_set_card_data(self):
        self.erase_db()
        self.populate_db(2)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            card_list = db_getter_connection.get_all_set_card_data(
                {co.SET_NAME_COLUMN: "Aquapolis"}
            )
            assert len(card_list) == 186
            card_list = db_getter_connection.get_all_set_card_data(
                {co.SET_NAME_COLUMN: "Arceus"}
            )
            print(len(card_list))
            assert len(card_list) == 111

    def test_search_card_names(self):
        self.erase_db()
        self.populate_db(1)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            card_list = db_getter_connection.search_card_names(
                {co.CARD_NAME_COLUMN: "Ai"}
            )
            print(card_list)
        assert len(card_list) == 3
        assert card_list[0].get(co.CARD_NAME_COLUMN) == "Aipom"
        assert card_list[1].get(co.CARD_NAME_COLUMN) == "Rainbow Energy"
        assert card_list[2].get(co.CARD_NAME_COLUMN) == "Remoraid"

    def test_get_sets(self):
        self.erase_db()
        self.populate_db(2)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            print(db_getter_connection.get_sets())

    def test_get_queries(self):
        self.erase_db()
        self.populate_db(2)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            query_aquapolis = db_getter_connection.query_cards("Aquapolis", "Price: Low - High", "", "",
                                                               "").get("set_card_list")
            query_arceus = db_getter_connection.query_cards("Arceus", "A-Z", "", "", "").get("set_card_list")
            query_card_names = db_getter_connection.query_cards("", "Price: Low - High", "ai", "",
                                                                "").get("set_card_list")
            query_aquapolis_card_names = db_getter_connection.query_cards("Aquapolis", "Price: High - Low", "ai", "",
                                                                          "").get("set_card_list")
            query_all_price_high = db_getter_connection.query_cards("", "Price: High - Low", "", "",
                                                                    "").get("set_card_list")
        # print(len(query_aquapolis))
        # print(len(query_arceus))

        assert len(query_aquapolis) == 186
        last_price = 0
        for query in query_aquapolis:
            # print(query)
            assert query["set_name"] == "Aquapolis"
            assert query["price"] >= last_price
            last_price = query["price"]

        assert len(query_arceus) == 111
        last_card_name = ""
        for query in query_arceus:
            # print(query)
            assert query["set_name"] == "Arceus"
            assert query["card_name"] > last_card_name
            last_card_name = query["card_name"]

        assert len(query_all_price_high) == 297
        last_price = sys.float_info.max
        for query in query_all_price_high:
            assert query["price"] <= last_price
            last_price = query["price"]

        assert len(query_card_names) == 4
        last_price = 0
        for query in query_card_names:
            # print(query)
            assert "ai" in query["card_name"].lower()
            assert query["price"] >= last_price
            last_price = query["price"]

        assert len(query_aquapolis_card_names) == 3
        last_price = sys.float_info.max
        for query in query_aquapolis_card_names:
            print(query)
            assert "ai" in query["card_name"].lower()
            assert query["price"] <= last_price
            last_price = query["price"]

    def test_chilling_reign(self):
        self.erase_db()
        self.populate_specific_set_data("SWSH06 Chilling Reign")

    def test_call_of_legends(self):
        self.erase_db()
        self.populate_specific_set_data("Call of Legends")

    def test_alphabetical(self):
        self.erase_db()
        self.populate_specific_set_data("Jungle")
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            query_jungle = db_getter_connection.query_cards("Jungle", "A-Z", "", "", "").get("set_card_list")
        # print(json.dumps(query_jungle, indent=4))
        assert len(query_jungle) == 64
        last_card_name = ""
        for query in query_jungle:
            print(query)
            assert query["set_name"] == "Jungle"
            assert query["card_name"] >= last_card_name
            last_card_name = query["card_name"]

    def test_get_all_set_counts(self):
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            set_list = db_getter_connection.get_sets()
            for set_item in set_list:
                print(
                    f"{db_getter_connection.get_set_card_count(set_item)}, {set_item.get(co.SET_NAME_COLUMN)}",
                )
                # print(set_item)
            # query_jungle = db_getter_connection.query_cards(
            #     "Jungle", "A-Z", "", ""
            # ).get("set_card_list")

    def test_get_queries_sums(self):
        self.erase_db()
        self.populate_db(1)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            query = db_getter_connection.query_cards("", "Price: Low - High", "", "", "")
            query_want = db_getter_connection.query_cards("", "Price: Low - High", "", "want", "")
            query_have = db_getter_connection.query_cards("", "Price: Low - High", "", "have", "")
        print(json.dumps(query_want, indent=4))
        print(json.dumps(query_have, indent=4))

        assert query["count_want"] == 160
        assert query["count_have"] == 29
        assert query["sum_price"] == 7172.389999999993

    def test_update_have_want(self):
        self.erase_db()
        self.populate_db(1)
        card_id_dict = {common_objects.TCGP_ID_COLUMN: 83487}
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            base_query = db_getter_connection.get_card_from_id(card_id_dict)
            assert base_query[common_objects.STATE_WANT_COLUMN] == 1
            assert base_query[common_objects.STATE_HAVE_COLUMN] == 0
            assert base_query[common_objects.STATE_GIFT_COLUMN] == 0
            db_getter_connection.increase_want(card_id_dict)
            card_data_query = db_getter_connection.get_card_from_id(card_id_dict)
            assert card_data_query[common_objects.STATE_WANT_COLUMN] == 2
            db_getter_connection.decrease_want(card_id_dict)
            db_getter_connection.decrease_want(card_id_dict)
            card_data_query = db_getter_connection.get_card_from_id(card_id_dict)
            assert card_data_query[common_objects.STATE_WANT_COLUMN] == 0
            db_getter_connection.increase_have(card_id_dict)
            db_getter_connection.increase_have(card_id_dict)
            card_data_query = db_getter_connection.get_card_from_id(card_id_dict)
            assert card_data_query[common_objects.STATE_HAVE_COLUMN] == 2
            db_getter_connection.decrease_have(card_id_dict)
            card_data_query = db_getter_connection.get_card_from_id(card_id_dict)
            assert card_data_query[common_objects.STATE_HAVE_COLUMN] == 1
            db_getter_connection.gifted(card_id_dict)
            card_data_query = db_getter_connection.get_card_from_id(card_id_dict)
            assert card_data_query[common_objects.STATE_GIFT_COLUMN] == 1

        print(json.dumps(base_query, indent=4))

        assert base_query[common_objects.CARD_NAME_COLUMN] == "Aipom"
        assert base_query[common_objects.STATE_HAVE_COLUMN] == 0
        assert base_query[common_objects.STATE_WANT_COLUMN] == 1

    def test_download_card_icons(self):
        # self.erase_db()
        # with DBCreator(co.DBType.PHYSICAL) as db_connection:
        #     db_connection.create_db()
        #     for set_data in load_set_data_dir(self.DATA_PATH):
        #         db_connection.add_set_card_data(set_data)
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            # query = db_getter_connection.query_cards("", "", "", "")
            query = db_getter_connection.get_all_ids()
            # query_want = db_getter_connection.query_cards("", "", "", "want")
            # query_have = db_getter_connection.query_cards("", "", "", "have")
        # print(json.dumps(query, indent=4))
        id_list = [card_data[common_objects.TCGP_ID_COLUMN] for card_data in query]
        # print(len(id_list))
        download_tcgp_card_images(id_list)

    def test_get_query_all(self):
        with DatabaseHandler(co.DBType.PHYSICAL) as db_getter_connection:
            # query = db_getter_connection.query_cards("", "", "", "")
            query = db_getter_connection.get_all_ids()
            # query = db_getter_connection.get_test()
            # query_want = db_getter_connection.query_cards("", "", "", "want")
            # query_have = db_getter_connection.query_cards("", "", "", "have")
        # print(json.dumps(query, indent=4))
        id_list = [card_data[common_objects.TCGP_ID_COLUMN] for card_data in query]
        print(len(id_list))
        # print(json.dumps(query_have, indent=4))

        # print(query["count_have"])
        # print(query["count_want"])
        # print(query["price_want"])
        # print(query["price_have"])
        # print(query["sum_price"])
        # print(query["count_cards"])
        # print(query["percent_complete"])

        # assert query["count_want"] == 160
        # assert query["count_have"] == 29
        # assert query["sum_price"] == 7172.389999999993
