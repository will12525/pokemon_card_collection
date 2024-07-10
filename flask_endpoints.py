import pathlib
import os
from enum import Enum
from flask import Response
from flask import Flask, request, render_template, jsonify

from database_handler import common_objects
from database_handler.common_objects import DBType
from database_handler.db_getter import DatabaseHandler
from database_handler.db_setter import DBCreator
from database_handler.input_file_parser import load_set_data_dir

# USERS
# There are two users
#       Willow
#               Can update all states
#               Can view HAVE
#               Can view WANT
#       Tori
#               Can update GIFT
#               Can view all cards
# Be able to change the current user
#
# VIEWS
# ALWAYS Hide gifted cards
#       Unless Tori is User
# Display a list of all pokemon cards
# Display all cards by set
#       Be able to change the viewed set

# CARDS
# Have a Have, Want, Gift Mark
# Be able to change want to have
#       Unless Tori is user
# Be able to mark a card as gifted
#       Unless Willow is user
#       Be able to remove gifted mark


app = Flask(__name__)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True


class APIEndpoints(Enum):
    MAIN = "/"
    GET_SET_CARD_LIST = "/get_set_card_list"
    UPDATE_HAVE = "/update_have"
    UPDATE_WANT = "/update_want"
    GIFTED = "/gifted"
    UPDATE_CARD_INDEX = "/update_card_index"


DB_PATH = "data_files/set_htmls/"


def setup_db():
    # if os.path.exists(DB_PATH):
    #     os.remove(DB_PATH)
    with DBCreator(DBType.PHYSICAL) as db_connection:
        db_connection.create_db()
        for set_data in load_set_data_dir(DB_PATH):
            db_connection.add_set_card_data(set_data)


@app.route(APIEndpoints.MAIN.value)
def index():
    with DatabaseHandler() as db_getter_connection:
        python_metadata = {
            "set_list": db_getter_connection.get_sets(),
        }
    return render_template("index.html", python_metadata=python_metadata)


@app.route(APIEndpoints.GET_SET_CARD_LIST.value, methods=["POST"])
def get_set_card_list():
    data = {}
    if json_request := request.get_json():
        with DatabaseHandler() as db_getter_connection:
            data.update(
                db_getter_connection.query_cards(json_request.get(common_objects.SET_NAME_COLUMN),
                                                 json_request.get("filter_str"),
                                                 json_request.get("card_name_search_query"),
                                                 json_request.get("filter_ownership"),
                                                 json_request.get("card_season_search_query")))
            data["set_list"] = db_getter_connection.get_sets()
    return jsonify(data), 200


@app.route(APIEndpoints.UPDATE_HAVE.value, methods=["POST"])
def update_have():
    data = {}
    if json_request := request.get_json():
        with DatabaseHandler() as db_getter_connection:
            db_getter_connection.set_have(json_request)
    return jsonify(data), 200


@app.route(APIEndpoints.UPDATE_WANT.value, methods=["POST"])
def update_want():
    data = {}
    if json_request := request.get_json():
        with DatabaseHandler() as db_getter_connection:
            db_getter_connection.set_want(json_request)
    return jsonify(data), 200


@app.route(APIEndpoints.GIFTED.value, methods=["POST"])
def gifted():
    data = {}
    if json_request := request.get_json():
        with DatabaseHandler() as db_getter_connection:
            db_getter_connection.gifted(json_request)
    return jsonify(data), 200


@app.route(APIEndpoints.UPDATE_CARD_INDEX.value, methods=["POST"])
def update_card_index():
    data = {}
    if json_request := request.get_json():
        with DatabaseHandler() as db_getter_connection:
            print(json_request)
            db_getter_connection.set_card_index(json_request)
    return jsonify(data), 200


#
# @app.route("/video_feed")
# def video_feed():
#     return Response(camera_control.get_live_frame(), mimetype="multipart/x-mixed-replace; boundary=frame")
#
#
# @app.route("/increase_focus", methods=['POST'])
# def increase_focus():
#     camera_control.increase_focus()
#     return {}, 200
#
#
# @app.route("/decrease_focus", methods=['POST'])
# def decrease_focus():
#     camera_control.decrease_focus()
#     return {}, 200
#
#
# @app.route("/set_auto_focus", methods=['POST'])
# def set_auto_focus():
#     camera_control.set_auto_focus()
#     return {}, 200
#
# @app.route("/zero_focus", methods=['POST'])
# def zero_focus():
#     camera_control.zero_focus()
#     return {}, 200

# setup_db()

if __name__ == "__main__":
    print("--------------------Running Main--------------------")
    # app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
