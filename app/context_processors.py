"""Context processors for the Flask application."""

import random

_FOOD_ICONS = (
    "🍇 🍈 🍊 🍋 🍌 🍍 🥭 🍎 🍐 🍑 🍒 🍓 🫐 🍅 🫒 🥑 🍆 🥕 🌽 🌶️ "
    "🫑 🥒 🥦 🧄 🧅 🥜 🫚 🫛 🍞 🥐 🥨 🧇 🧀 🍗 🥩 🥓 🍔 🍟 🍕 🌭 "
    "🥪 🌮 🌯 🫔 🥗 🍿 🥫 🍝 🍱 🍙 🍜 🍣 🍤 🍥 🥮 🥟 🥠 🍦 🍩 🍪 "
    "🍰 🧁 🍫 🍬 🍭 🍵 🍾 🍷 🍹 🧋 🧃"
).split()


def register_context_processors(app):
    @app.context_processor
    def inject_food_icon():
        return {"current_food_icon": random.choice(_FOOD_ICONS)}
