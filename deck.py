import os
import json
import pprint
from bs4 import BeautifulSoup as bs

import set_order
import set_info
import card_info


def read_file(file_path):
    with open(file_path, "r") as f:
        output = f.read()
    return output


def get_set_from_list(set_name, set_list):
    for set_data in set_list:
        if set_data.get_set_name() == set_name:
            return set_data
    return None


def round_float_for_print(value_to_round):
    return "{:.2f}".format(value_to_round)


class Deck:

    def __init__(self, data_file, exclude_swsh=False):
        self.cards = []
        split_path = os.path.splitext(data_file)
        if split_path[1] == ".html":
            self.setup_from_html(data_file)
        elif split_path[1] == ".json":
            print("Json file")
            self.setup_from_json(data_file, exclude_swsh)
        self.pp = pprint.PrettyPrinter(indent=4)

    def get_deck_size(self):
        return len(self.cards)

    def get_cards(self):
        return self.cards

    def add_card(self, card):
        self.cards.append(card)

    def check_for_dupes(self, compare_deck):
        deck_set_list = self.get_set_lists()
        compare_deck_set_list = compare_deck.get_set_lists()
        dupe_count = 0
        for deck_set in deck_set_list:
            set_name = deck_set.get_set_name()
            compare_deck_set = get_set_from_list(set_name, compare_deck_set_list)
            if compare_deck_set:
                for card in deck_set.get_card_list():
                    for compare_card in compare_deck_set.get_card_list():
                        if card.compare(compare_card):
                            print("The below two cards match:")
                            card.print_data()
                            print("And:")
                            compare_card.print_data()
                            print("\n")
                            dupe_count += 1
        print(f"Dupes found: {dupe_count}")

    def get_set_lists(self):
        set_list = []
        for i in range(set_order.get_set_count()):
            set_item = set_info.SetData(i, set_order.get_set_name_by_index(i))
            set_list.append(set_item)

        for card in self.cards:
            set_location = set_order.get_set_index_by_name(card.get_set())
            if set_location:
                set_list[set_location].add_card(card)
        return set_list

    def tally_cards_in_all_sets_my_sheet(self):
        set_list = self.get_set_lists()
        # We're changing the order of the main deck. Update oldest first. This needs re-work to get by tag, not location
        old_set = set_list.pop(
            set_order.get_set_index_by_name("SWSH12: Silver Tempest Trainer Gallery")
        )
        merge_set_loc = set_order.get_set_index_by_name("SWSH12: Silver Tempest")
        set_list[merge_set_loc].merge_set_with(old_set)

        old_set = set_list.pop(
            set_order.get_set_index_by_name("SWSH11: Lost Origin Trainer Gallery")
        )
        merge_set_loc = set_order.get_set_index_by_name("SWSH11: Lost Origin")
        set_list[merge_set_loc].merge_set_with(old_set)

        old_set = set_list.pop(
            set_order.get_set_index_by_name("SWSH10: Astral Radiance Trainer Gallery")
        )
        merge_set_loc = set_order.get_set_index_by_name("SWSH10: Astral Radiance")
        set_list[merge_set_loc].merge_set_with(old_set)

        old_set = set_list.pop(
            set_order.get_set_index_by_name("SWSH09: Brilliant Stars Trainer Gallery")
        )
        merge_set_loc = set_order.get_set_index_by_name("SWSH09: Brilliant Stars")
        set_list[merge_set_loc].merge_set_with(old_set)

        old_set = set_list.pop(
            set_order.get_set_index_by_name("Legendary Treasures: Radiant Collection")
        )
        merge_set_loc = set_order.get_set_index_by_name("Legendary Treasures")
        set_list[merge_set_loc].merge_set_with(old_set)

        return set_list

    def setup_from_json(self, file_path, exclude_swsh=False):
        for card in json.loads(read_file(file_path)):
            card_obj = card_info.CardData()
            card_obj.load_json(card)
            if exclude_swsh and "SWSH" in card_obj.get_set():
                continue
            else:
                self.cards.append(card_obj)

    def setup_from_html(self, file_path):
        soup = bs(read_file(file_path), "html.parser")
        t_body = list(soup.children)[0]
        for items in list(t_body.children):
            card_obj = card_info.CardData()
            card_obj.load_html(items)
            self.cards.append(card_obj)

    def deck_as_list(self):
        json_card_list = []
        for card in self.cards:
            json_card_list.append(card.to_json())
        return json_card_list

    def output_deck_to_json(self):
        print(json.dumps(self.deck_as_list(), indent=4))

    def save_deck_to_json(self, filename):
        json_card_list = self.deck_as_list()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(json_card_list, f, ensure_ascii=True, indent=4)

    def print_tally_price_ranges(self):
        # 0 = n <= $1, 1 = $1 < n <= $5, 2 = $5 < n <= $10, 3 = $10 < n <= $25,  4 = $25 < n <= $50,
        # 5 = $50 < n <= $100, 6 = $100 < n <= $500,  7 = $500 < n <= $1000, 8 = $1000 < n, 9 = invalid state
        price_ranges = [0] * 10
        price_sums = [0] * 10
        for card in self.cards:
            cost = card.get_cost()
            loc = 0
            if cost <= 1:
                loc = 0
            elif 1 < cost <= 5:
                loc = 1
            elif 5 < cost <= 10:
                loc = 2
            elif 10 < cost <= 25:
                loc = 3
            elif 25 < cost <= 50:
                loc = 4
            elif 50 < cost <= 100:
                loc = 5
            elif 100 < cost <= 500:
                loc = 6
            elif 500 < cost <= 1000:
                loc = 7
            elif 1000 < cost:
                loc = 8
            else:
                loc = 9
            price_ranges[loc] += 1
            price_sums[loc] += cost

        # for price in price_ranges:
        print(
            f"$1>=\t: {price_ranges[0]},\t Cost: {round_float_for_print(price_sums[0])}"
        )
        print(
            f"$5>=\t: {price_ranges[1]},\t Cost: {round_float_for_print(price_sums[1])}"
        )
        print(
            f"$10>=\t: {price_ranges[2]},\t Cost: {round_float_for_print(price_sums[2])}"
        )
        print(
            f"$25>=\t: {price_ranges[3]},\t Cost: {round_float_for_print(price_sums[3])}"
        )
        print(
            f"$50>=\t: {price_ranges[4]},\t Cost: {round_float_for_print(price_sums[4])}"
        )
        print(
            f"$100>=\t: {price_ranges[5]},\t Cost: {round_float_for_print(price_sums[5])}"
        )
        print(
            f"$500>=\t: {price_ranges[6]},\t Cost: {round_float_for_print(price_sums[6])}"
        )
        print(
            f"$1000>=\t: {price_ranges[7]},\t Cost: {round_float_for_print(price_sums[7])}"
        )
        print(
            f"$1000<\t: {price_ranges[8]},\t Cost: {round_float_for_print(price_sums[8])}"
        )
        print(sum(price_ranges))

    def print_ordered_sets_card_count(self):
        for tcg_set in self.get_set_lists():
            tcg_set.print_set_info()

    def print_cards(self):
        for card in self.cards:
            card.print_data()
