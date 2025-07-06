import os
import requests
from flask import Flask, jsonify, request

app = Flask('name')

API_TOKEN = os.environ.get("CR_API_TOKEN")   # Set this in Render Dashboard

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


@app.route("/get-deck", methods=["POST"])
def get_deck():
    try:
        print('running')
        data = request.get_json()
        medals = int(data.get('medals'))
        print(medals)

        # Step 1: Get leaderboard players
        limit = 300
        CR_API_BASE_URL = "https://api.clashroyale.com/v1"
        leaderboard_url = f"{CR_API_BASE_URL}/locations/global/pathoflegend/players?limit={limit}"
        res = requests.get(leaderboard_url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            return jsonify({"error": f"Leaderboard fetch failed: {res.status_code} (reason: {res.reason})"}), 500

        players = res.json().get("items", [])
        print('first player:')
        print(players[0] if players else "No players found")

        # Step 2: Match exact medals and fetch deck
        for player in players:
            if player.get("eloRating") == medals:
                print('found player with exact medals')
                tag = player["tag"].replace("#", "%23")
                battle_url = f"https://api.clashroyale.com/v1/players/{tag}/battlelog"
                battle_res = requests.get(battle_url, headers=HEADERS, timeout=10)

                if battle_res.status_code != 200:
                    return jsonify({"error": "Battle log fetch failed"}), 500

                battles = battle_res.json()
                for battle in battles:
                    if battle["gameMode"]['name'] == "Ranked1v1_NewArena2":
                        print('battle has good type')
                        deck = [{"name": c["name"], "level": c["level"]} for c in battle["team"][0]["cards"]]

                        # ✅ Pretty table-style output without levels
                        print("\n🃏 Deck:")
                        print("+" + "-" * 24 + "+")
                        for i, card in enumerate(deck, start=1):
                            print(f"| {i}. {card['name']:<20}|")
                        print("+" + "-" * 24 + "+\n")

                        return jsonify({"deck": deck})

        return jsonify({"error": "Player not found with exact medals"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Backend is Running"


if __name__ == "__main__":
    app.run()
