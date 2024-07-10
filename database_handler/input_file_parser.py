import json
import os
import pathlib
import time

import requests
from bs4 import BeautifulSoup
import re
from deck import read_file
from . import common_objects


class TableDataExtractor:
    """Extracts table data from a webpage."""

    data_dir = "downloaded_images"  # Directory to store downloaded images

    # Create the directory if it doesn't exist
    def __init__(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def extract_table_data(self, html_soup):
        """Fetches the webpage, parses the HTML, and extracts data from the first table.

        Returns:
            A list of dictionaries, where each dictionary represents a row (tr) containing data from the first table (td elements).
            An empty list is returned if no table is found.
        """
        table = html_soup.find("tbody")

        # Check if table exists
        if not table:
            return []

        # Extract headers and table data
        table_data = []
        headers = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])

            # Extract headers from the first row
            if not headers:
                for cell in cells:
                    headers.append(cell.text.strip().replace(" ", ""))
                continue

            # Extract data for each cell based on headers
            row_dict = {}
            for i, cell in enumerate(cells):
                if i < len(headers):
                    row_dict[headers[i]] = cell.text.strip()

                    a_tag = cell.find("a")
                    # print(a_tag)

            table_data.append(row_dict)
        return table_data

    def extract_card_data(self, html_soup):
        """Fetches the webpage, parses the HTML, and extracts data from the first table.

        Returns:
            A list of dictionaries, where each dictionary represents a row (tr) containing data from the first table (td elements).
            An empty list is returned if no table is found.
        """
        table_data = {}
        card_rarity_regex = "- \[(.+)\]$"
        card_index_division_regex = "- (\d+)/\d+"
        card_index_regex = " \((\d+)\)"

        table = html_soup.find("tbody")

        set_name = ""

        # Check if table exists
        if not table:
            return table_data

        # track_card_name = "Dugtrio"

        # Extract headers and table data
        for row in table.find_all("tr"):
            # track_card = False
            cells = row.find_all(["td", "th"])
            # Extract data for each cell based on headers
            row_dict = common_objects.default_card_dict.copy()
            row_dict[common_objects.STATE_HAVE_COLUMN] = int(cells[0].text.strip())
            row_dict[common_objects.STATE_WANT_COLUMN] = int(cells[1].text.strip())

            if (
                    row_dict[common_objects.STATE_WANT_COLUMN] == 0
                    and row_dict[common_objects.STATE_HAVE_COLUMN] == 0
            ):
                row_dict[common_objects.STATE_WANT_COLUMN] = 1

            # if (
            #     row_dict[common_objects.STATE_HAVE_COLUMN]
            #     == row_dict[common_objects.STATE_WANT_COLUMN]
            #     == 0
            # ):
            #     row_dict[common_objects.STATE_WANT_COLUMN] = True
            row_dict[common_objects.CARD_NAME_COLUMN] = (
                cells[3].text.strip().replace("\n", "").replace("       ", "")
            )
            # if track_card_name in row_dict[common_objects.CARD_NAME_COLUMN]:
            #     track_card = True
            row_dict[common_objects.SET_NAME_COLUMN] = cells[4].text.strip()
            set_name = row_dict[common_objects.SET_NAME_COLUMN]
            row_dict[common_objects.SET_INDEX_COLUMN] = common_objects.get_set_index(
                row_dict[common_objects.SET_NAME_COLUMN]
            )

            row_dict[common_objects.PRICE_COLUMN] = float(
                cells[6].text.strip().replace("$", "").replace(",", "")
            )

            if row_dict[common_objects.PRICE_COLUMN] == 0:
                # if track_card:
                #     print(row_dict)
                #     print("price 0")
                # print(row_dict)
                continue

            if card_rarity_search := re.search(
                    card_rarity_regex, row_dict[common_objects.CARD_NAME_COLUMN]
            ):
                row_dict[common_objects.CARD_RARITY_COLUMN] = (
                    card_rarity_search.groups()[-1]
                )
                row_dict[common_objects.CARD_NAME_COLUMN] = row_dict[
                                                                common_objects.CARD_NAME_COLUMN
                                                            ][: card_rarity_search.span()[0]].strip()
            if card_index_search := re.search(
                    card_index_division_regex, row_dict[common_objects.CARD_NAME_COLUMN]
            ):
                # print(f"Division: {card_index_search.groups()[0]}")
                row_dict[common_objects.CARD_INDEX_COLUMN] = int(
                    card_index_search.groups()[0]
                )
                row_dict[common_objects.CARD_NAME_COLUMN] = row_dict[
                                                                common_objects.CARD_NAME_COLUMN
                                                            ][: card_index_search.span()[0]].strip()
                # print(
                #     row_dict[common_objects.CARD_NAME_COLUMN],
                #     row_dict[common_objects.CARD_INDEX_COLUMN],
                # )
            if card_index_search := re.search(
                    card_index_regex, row_dict[common_objects.CARD_NAME_COLUMN]
            ):
                row_dict[common_objects.CARD_INDEX_COLUMN] = int(
                    card_index_search.groups()[0]
                )
                row_dict[common_objects.CARD_NAME_COLUMN] = row_dict[
                                                                common_objects.CARD_NAME_COLUMN
                                                            ][: card_index_search.span()[0]].strip()

                # print(
                #     row_dict[common_objects.CARD_NAME_COLUMN],
                #     row_dict[common_objects.CARD_INDEX_COLUMN],
                # )

            url_card_link = row.find("a").get("href")
            if url_card_link:
                url_card_link_list = url_card_link.split("/")
                row_dict[common_objects.TCGP_ID_COLUMN] = int(url_card_link_list[-2])
                row_dict[common_objects.TCGP_PATH_COLUMN] = url_card_link_list[
                    -1
                ].split("-", 1)[1]
            else:
                # if track_card:
                #     print(row_dict)
                #     print("no card link")
                continue

            if "Code Card - " in row_dict[common_objects.CARD_NAME_COLUMN]:
                # if track_card:
                #     print(row_dict)
                #     print("code card")
                continue

            tcgp_id = row_dict[common_objects.TCGP_ID_COLUMN]
            if tcgp_id in table_data:
                # print("DUPE!")
                # print(row_dict[common_objects.PRICE_COLUMN])
                # print(table_data[filter_combo][common_objects.PRICE_COLUMN])
                result = min(
                    row_dict[common_objects.PRICE_COLUMN],
                    table_data[tcgp_id][common_objects.PRICE_COLUMN],
                )
                # print(result)
                if result == row_dict[common_objects.PRICE_COLUMN]:
                    # if track_card:
                    #     print(row_dict)
                    #     print("Swapping item")
                    table_data[tcgp_id] = row_dict
                # else:
                # if track_card:
                #     print(row_dict)
                #     print("Ignoring")
            else:
                # if track_card:
                #     print(row_dict)
                #     print("Added new item")
                table_data[tcgp_id] = row_dict

        # for i in table_data:
        #     print(i, table_data[i])
        # print(
        #     f"Actual: {len(table_data)}, Expected: {common_objects.get_set_card_count(set_name)}"
        # )
        # print(json.dumps(table_data, indent=4))
        print(common_objects.get_set_card_count(set_name) - len(table_data), set_name)
        # assert len(table_data) == common_objects.get_set_card_count(set_name)
        return table_data

    #
    # def extract_set_codes(self, html_soup):
    #     set_codes = {}
    #     for div in html_soup.find_all("div", class_="set-glossary__setCode"):
    #         div_text = div.get_text(strip=True)
    #         x = re.search("\[.+\]$", div_text)
    #         set_code = div_text[x.span()[0] + 1 : x.span()[1] - 1]
    #         if set_code in self.excluded_set_codes:
    #             continue
    #         set_name = div_text[: x.span()[0] - 1]
    #         # print('"' + set_name + '"' + ":None,")
    #         serebii_set_name = self.ptcg_set_names_to_serebii.get(set_name)
    #         if not serebii_set_name:
    #             #     print(f"Found set match!: {set_name}, {serebii_set_name}")
    #             # else:
    #             print(f"Missing!: {set_name}, {set_code}")
    #
    #         # match_found = False
    #         # for set in table_data:
    #         #     if set["SetName"] == set_name:
    #         #         match_found = True
    #         #         print(f'"{set_name}":"{set["SetName"]}",')
    #         #         # print(f"Found set match!: {set_name}")
    #         set_codes[set_name] = {"set_code": set_code}
    #         # if not match_found:
    #         #     print(f'"{set_name}":None,')
    #
    #         # print(f"Failed to find set match!: {set_name}")
    #
    #     return set_codes
    def load_tcg_card_webpage(self, card_tcgp_id, card_tcgp_name):
        url = (
            f"https://www.tcgplayer.com/product/{card_tcgp_id}/pokmeon-{card_tcgp_name}"
        )
        print(url)

    def download_tcg_image(self, card_tcgp_id):
        url = f"https://tcgplayer-cdn.tcgplayer.com/product/{card_tcgp_id}_200w.jpg"
        self.download_image(url, f"{card_tcgp_id}.jpg")

    def download_images(self, url, html_soup):
        images = html_soup.find_all("img")
        for img in images:
            if img and "src" in img.attrs:
                if ".png" in img["src"]:
                    domain_parts = url.split("/", maxsplit=3)
                    source_url = "/".join(domain_parts[:3]) + img["src"]
                    destination_file_name = img["src"].rsplit("/", maxsplit=1)[-1]
                    # Remove the last element (assuming it's a filename or directory)
                    self.download_image(source_url, destination_file_name)

    def download_image(self, image_source_url, image_destination_path):
        """Downloads an image from the given URL and saves it to the specified filename, only if the file doesn't exist.

        Args:
            image_source_url: The URL of the image to download.
            image_destination_path: The filename to save the downloaded image as.
        """
        print(image_source_url, image_destination_path)
        try:
            # Check if the image file already exists
            image_path = os.path.join(self.data_dir, image_destination_path)
            if not os.path.isfile(image_path):
                # Download the image data only if the file doesn't exist
                image_response = requests.get(image_source_url, stream=True)
                image_response.raise_for_status()

                # Save the image to the specified file
                with open(image_path, "wb") as f:
                    for chunk in image_response.iter_content(1024):
                        f.write(chunk)

                print(f"Image downloaded: {image_destination_path}")
                time.sleep(0.5)
            else:
                print(f"Image already exists: {image_destination_path}")
        except Exception as e:
            print(f"Error downloading image: {e}")


def download_tcgp_card_images(tcgp_id_list):
    extractor = TableDataExtractor()
    for index, tcgp_id in enumerate(tcgp_id_list):
        extractor.download_tcg_image(tcgp_id)
        percent_complete = round((index / len(tcgp_id_list) * 100), 2)
        print(f"Status: {percent_complete}%")


def get_html_soup_from_path(file_path):
    return BeautifulSoup(read_file(file_path), "html.parser")


def get_html_soup_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if request fails

    # Parse the HTML content
    return BeautifulSoup(response.content, "html.parser")


def load_set_data(file_name):
    extractor = TableDataExtractor()
    set_soup = get_html_soup_from_path(file_name)
    return extractor.extract_card_data(set_soup)


def load_set_data_dir(folder_path):
    # set_data_soup = get_html_soup_from_path(set_data_file_path)
    # set_codes_soup = get_html_soup_from_path(set_codes_file_path)
    # table_data = extractor.extract_table_data(set_data_soup)
    # extractor.download_images(url, set_data_soup)
    set_htmls_path = pathlib.Path(folder_path)
    for editor_mp4_file in list(sorted(set_htmls_path.rglob("*.html"))):
        yield load_set_data(editor_mp4_file)
        # set_soup = get_html_soup_from_path(editor_mp4_file)
        # set_data = extractor.extract_card_data(set_soup)
        # # print(set_data)
        # yield set_data


def get_sbi_set_data():
    # Pass in the name of the set
    pass

#
# def main():
#     url = "https://serebii.net/card/english.shtml"  # Replace with your target URL
#     set_data_file_path = "../data_files/set_data.html"
#     set_codes_file_path = "../data_files/set_codes.html"
#
#     # Create a data collector object
#     extractor = TableDataExtractor()
#     # set_codes_soup = get_html_soup_from_path(set_codes_file_path)
#     # table_data = extractor.extract_table_data(set_data_soup)
#     # extractor.download_images(url, set_data_soup)
#     set_htmls_path = pathlib.Path("../data_files/set_htmls/")
#     for editor_mp4_file in list(sorted(set_htmls_path.rglob("*.html"))):
#         set_soup = get_html_soup_from_path(editor_mp4_file)
#         table_data = extractor.extract_card_data(set_soup)
#
#         # Extract table data and download images
#         if table_data:
#             # for table in table_data:
#             #     print(table, table_data[table])
#             # Insert data into the database table
#             db_connection.insert_data_into_table(table_name, table_data)
#             print("Data extracted and stored in database.", editor_mp4_file)
#             break
#         else:
#             print("No table found.")
#
#     print(db_connection.get_all_data())
#     # Close the database connection
#     db_connection.close_connection()

#
# if __name__ == "__main__":
#     main()
