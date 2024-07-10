class SetData:

    def __init__(self, index, name):
        self.index = index
        self.name_str = name
        self.total_cards = 0
        self.total_cost = 0
        self.card_list = []

    def add_card(self, card):
        self.card_list.append(card)

    def get_index(self):
        return self.index

    def get_set_name(self):
        return self.name_str

    def get_total_cards(self):
        return len(self.card_list)

    def get_total_cost(self):
        total_cost = 0
        for card in self.card_list:
            total_cost += card.get_cost()
        return round(total_cost, 2)

    def get_card_list(self):
        return self.card_list

    def print_set_info(self):
        print(f"Index: {self.index+1}, Name: {self.name_str}, Cards: {self.get_total_cards()}, "
              f"Cost: {self.get_total_cost()}")

    def merge_set_with(self, merge_set):
        for card in merge_set.get_card_list():
            self.add_card(card)
