from flask import Blueprint, jsonify, request

from chatbot.engine import ASSISTANT


assistant = Blueprint("assistant", __name__)


@assistant.route("/api/assistant", methods=["POST"])
def reply():

    payload = request.get_json(silent=True) or {}

    message = payload.get("message", "")

    result = ASSISTANT.get_reply(message)

    return jsonify(result)
