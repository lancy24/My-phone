from random import shuffle

import streamlit as st

from gallery_app import list_images


def new_game():
    deck = list(range(6)) * 2
    shuffle(deck)
    st.session_state.memory = {
        "deck": deck,
        "open": [],
        "matched": [],
        "moves": 0,
        "photos": list_images()[:6],
    }


def reveal(index):
    game = st.session_state.memory

    if len(game["open"]) == 2:
        game["open"] = []

    game["open"].append(index)

    if len(game["open"]) == 2:
        first, second = game["open"]
        game["moves"] += 1
        if game["deck"][first] == game["deck"][second]:
            game["matched"].extend(game["open"])
            game["open"] = []


def run():
    st.title("🃏 Memory Match")
    if "memory" not in st.session_state:
        new_game()

    st.button("New game", on_click=new_game)
    game = st.session_state.memory
    st.caption(f"{len(game['matched']) // 2}/6 pairs · {game['moves']} moves")

    symbols = ["🌙", "🎵", "🪴", "🧭", "⏱️", "📚"]

    for start in range(0, len(game["deck"]), 4):
        for col, index in zip(st.columns(4), range(start, start + 4)):
            card = game["deck"][index]

            if index in game["matched"] or index in game["open"]:
                if card < len(game["photos"]) and game["photos"][card].is_file():
                    col.image(str(game["photos"][card]), caption=f"Photo {card + 1}")
                else:
                    col.markdown(f"### {symbols[card]}")
            else:
                col.button(
                    f"Card {index + 1}",
                    key=f"memory_{index}",
                    on_click=reveal,
                    args=(index,),
                    use_container_width=True,
                )

    if len(game["matched"]) == len(game["deck"]):
        st.success(f"All pairs found in {game['moves']} moves!")