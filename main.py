import json
import time
import pyperclip as pc
import data_loader


def update_excel_file(set_list, print_cost=False):
    count = ""
    cost = ""
    for set_data in set_list:
        set_name = set_data.get_set_name()
        if set_name in ("Base set", "Base set 2"):
            if set_name == "Base set":
                count += "=$'old sets'.A37\n"
            elif set_name == "Base set 2":
                count += "=$'old sets'.G81\n"
            cost += "1000\n"
        else:
            count += f"{set_data.get_total_cards()}\n"
            cost += f"{set_data.get_total_cost()}\n"

    # print(cost)
    if print_cost:
        pc.copy(cost)
    else:
        pc.copy(count)

    print("Clipboard Ready")


def load_price_history():
    data_loader.get_specific_deck_from("path/")


def main():
    # Load from file
    want_deck = data_loader.get_want_deck()
    have_deck = data_loader.get_have_deck()

    update_excel_file(
        set_list=want_deck.tally_cards_in_all_sets_my_sheet(), print_cost=False
    )
    # want_deck.print_ordered_sets_card_count()
    # have_deck.print_ordered_sets_card_count()
    # want_deck.print_tally_price_ranges()
    # want_deck.print_ordered_sets_card_count()


def get_set_list():
    want_deck = data_loader.get_want_deck()
    want_deck.print_ordered_sets_card_count()


def search_want_deck_for_poke(name: str):
    want_deck = data_loader.get_want_deck()
    want_deck_list = want_deck.deck_as_list()
    for item in want_deck_list:
        if name in item.get("Name"):
            print(f'Set: {item.get("Set")}, Card: {item.get("Name")}')


def search_want_deck_for_set(set_name: str):
    want_deck = data_loader.get_want_deck()
    want_deck_list = want_deck.deck_as_list()
    for item in want_deck_list:
        if set_name in item.get("Set"):
            rarity = None

            if item.get("Secret"):
                rarity = "Secret"
            elif item.get("Full Art"):
                rarity = "Full Art"
            elif item.get("Alt Art"):
                rarity = "Alt art"

            if rarity:
                print(
                    f'Card: {item.get("Name")}, Rarity: {rarity}, Set: {item.get("Set")}'
                )
            else:
                print(f'Card: {item.get("Name")}, Set: {item.get("Set")}')


def print_wanted_pokemon_by_name():
    want_deck = data_loader.get_want_deck()
    want_deck_card_list = want_deck.deck_as_list()
    wanted_pokemon_by_name_dict = {}
    for card in want_deck_card_list:
        card_name = card.get("Name", None).lower()
        if card_name:
            if card_name not in wanted_pokemon_by_name_dict.keys():
                wanted_pokemon_by_name_dict[card_name] = 1
            else:
                wanted_pokemon_by_name_dict[card_name] = (
                    wanted_pokemon_by_name_dict.get(card_name) + 1
                )
        # print(card)
        # print(f'Card: {card.get("Name")}')

    print(json.dumps(wanted_pokemon_by_name_dict, indent=4))


def get_wanted_pokemon_by_name(pokemon_name: str):
    want_deck = data_loader.get_want_deck()
    want_deck_card_list = want_deck.deck_as_list()
    total_cost = 0
    for card in want_deck_card_list:
        # print(card)
        if pokemon_name in card.get("Name", "").lower():
            total_cost += card.get("cost")
            print(
                f'Card: {card.get("Name")}, Set: {card.get("Set")}, cost: {card.get("cost")}'
            )
    print(f"Sum of cost: ${round(total_cost)}")
    # print(len(want_deck_set_list))


if __name__ == "__main__":
    start_time = time.time()

    # print_wanted_pokemon_by_name()
    get_wanted_pokemon_by_name("wailord")
    main()
    # search_want_deck_for_set("Astral Radiance")
    # get_set_list()
    end_time = time.time()
    print(end_time - start_time)
