import os
import deck
from datetime import datetime
import json

data_files = "data_files"
new_want_data_file = f"{data_files}/new_want.html"
new_have_data_file = f"{data_files}/new_have.html"
record_folder = "auto_record/"
record_meta_data = f"{record_folder}/meta_data.json"


def save_as_json(my_deck, file_name):
    my_deck.save_deck_to_json(file_name)
    print("Deck saved to JSON file")


def read_file(file_path):
    with open(file_path, "r") as f:
        output = f.read()
    return output


def check_new_data(file_path):
    return os.stat(file_path).st_size > 0


def new_card_have_data():
    return check_new_data(new_have_data_file)


def new_card_want_data():
    return check_new_data(new_want_data_file)


def transfer_new_to_records(data_file, data_type):
    print("Found new data, transferring to records")
    card_deck = deck.Deck(data_file)
    date_stamp = datetime.today().strftime("%Y_%m_%d")
    new_file_name = f"{data_type}_{date_stamp}.json"
    new_file_path = f"{record_folder}{new_file_name}"
    if not os.path.exists(new_file_path):
        # Save deck to records
        save_as_json(card_deck, new_file_path)
        # Update the meta data with latest file
        meta_data = json.loads(read_file(record_meta_data))
        meta_data[f"latest_{data_type}_file"] = new_file_name
        with open(record_meta_data, "w") as outfile:
            json.dump(meta_data, outfile)
    else:
        print(f"ERROR: Output file already exists for new data\n{new_file_path}")
    # erase the file contents
    open(f"data_files/new_{data_type}.html", "w").close()
    return card_deck


def transfer_new_have_to_records():
    return transfer_new_to_records(new_have_data_file, "have")


def transfer_new_want_to_records():
    return transfer_new_to_records(new_want_data_file, "want")


def load_newest(data_type):
    meta_data = json.loads(read_file(record_meta_data))
    latest_file = meta_data.get(f"latest_{data_type}_file", "")
    if latest_file:
        latest_path = f"{record_folder}{latest_file}"
        print(f"Loading file from {latest_file}")
        return deck.Deck(latest_path)
    else:
        print("Latest file doesnt exist")
        return None


def load_newest_have():
    return load_newest("have")


def load_newest_want():
    return load_newest("want")


def get_want_deck():
    if new_card_want_data():
        print("Saving want deck")
        return transfer_new_want_to_records()
    else:
        return load_newest_want()


def get_have_deck():
    if new_card_have_data():
        print("Saving have deck")
        return transfer_new_have_to_records()
    else:
        return load_newest_have()


def get_specific_deck_from(data_file):
    deck.Deck(data_file)
