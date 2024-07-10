import re


def regex_search(regex, string):
    result = re.search(regex, string)
    if result:
        return result.group(1)


class CardData:

    def __init__(self):
        self.have = 0
        self.want = 0
        self.full_card_name = ""
        self.card_name = ""
        self.img_link = ""
        self.url = ""
        self.set_name = ""
        self.avg_cost = 0.0
        self.price_history = []

        self.specific_id = 0
        self.foil = False
        self.rFoil = False
        self.full_art = False
        self.alt_art = False
        self.secret = False

    def add_price_point(self, point):
        self.price_history.append(point)

    def get_name(self):
        return self.card_name

    def get_set(self):
        return self.set_name

    def get_cost(self):
        return self.avg_cost

    def get_id(self):
        return self.specific_id

    def get_url(self):
        return self.url

    def compare_rarity(self, compare_card):
        compare_card_rarity = compare_card.card_tags_to_json()
        if self.full_art == compare_card_rarity.get('Full Art', False) and \
                self.alt_art == compare_card_rarity.get('Alt Art', False) and \
                self.secret == compare_card_rarity.get('Secret', False):
            return True
        return False

    def compare(self, compare_card):
        if self.card_name == compare_card.get_name() and self.specific_id == compare_card.get_id()\
                and self.compare_rarity(compare_card) and self.url == compare_card.get_url() and self.have != self.want:
            return True
        return False

    def load_json(self, item_data):
        self.have = item_data['Have']
        self.card_name = item_data['Name']
        self.set_name = item_data['Set']
        self.have = item_data['Have']
        self.want = item_data['Want']
        self.img_link = item_data['img_link']
        self.url = item_data['url']
        self.card_tags_from_json(item_data)
        self.avg_cost = item_data['cost']

    def load_html(self, item_data):
        tags = list(item_data.children)
        self.have = tags[0].get_text()
        self.want = tags[1].get_text()
        self.full_card_name = tags[3].get_text().strip()
        self.extract_name_content()
        self.img_link = regex_search('image=\"(.+?)\"', str(tags[3]))
        self.url = regex_search('href=\"(.+?)\"', str(tags[3]))
        self.set_name = tags[4].get_text()
        self.avg_cost = float(tags[6].get_text().lstrip("$").replace(",", ""))

    def extract_name_content(self):
        # Fix here for porygon-z
        full_name_list = self.full_card_name.split(" - ")
        if len(full_name_list) > 1:
            foil = regex_search('\[(.+?)\]', full_name_list[1])
            if foil == "Holofoil":
                self.foil = True
            else:
                self.rFoil = True
        if "(" in full_name_list[0]:
            name_list = full_name_list[0].split("(", 1)
            self.card_name = name_list[0].strip()
            card_types = name_list[1]
            if "Alternate" in card_types:
                self.alt_art = True
            elif "Full Art" in card_types:
                self.full_art = True
            elif "Secret" in card_types:
                self.secret = True

            possible_number = re.search('\d+', card_types)
            if possible_number:
                self.specific_id = possible_number.group(0)
        else:
            self.card_name = full_name_list[0].strip()

    def print_data(self):
        print("Name:", self.card_name)
        print("Set:", self.set_name)
        tags = self.card_tags_to_json()
        if tags:
            print(tags)
        print("Have: ", self.have, "Want: ", self.want )
        print("img:", self.img_link)
        print("url:", self.url)
        print("cost:", self.avg_cost)

    def card_tags_to_json(self):
        ret_json = {}
        if self.specific_id != 0:
            ret_json['ID'] = self.specific_id
        if self.foil:
            ret_json['foil'] = self.foil
        elif self.rFoil:
            ret_json['Reverse Foil'] = self.rFoil
        if self.full_art:
            ret_json['Full Art'] = self.full_art
        elif self.alt_art:
            ret_json['Alt Art'] = self.alt_art
        elif self.secret:
            ret_json['Secret'] = self.secret
        return ret_json

    def card_tags_from_json(self, card_tag_data):
        if card_tag_data.get('ID'):
            self.specific_id = card_tag_data['ID']
        if card_tag_data.get('foil'):
            self.foil = card_tag_data['foil']
        elif card_tag_data.get('Reverse Foil'):
            self.rFoil = card_tag_data['Reverse Foil']
        if card_tag_data.get('Full Art'):
            self.full_art = card_tag_data['Full Art']
        elif card_tag_data.get('Alt Art'):
            self.alt_art = card_tag_data['Alt Art']
        elif card_tag_data.get('Secret'):
            self.secret = card_tag_data['Secret']

    def to_json(self):
        ret_json = {
            'Name': self.card_name,
            'Set': self.set_name,
            'Have': self.have,
            'Want': self.want,
            'img_link': self.img_link,
            'url': self.url,
            'cost': self.avg_cost
        }
        ret_json.update(self.card_tags_to_json())

        return ret_json