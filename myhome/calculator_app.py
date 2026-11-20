import streamlit as st


def press(key):
    s = st.session_state

    if key == "C":
        s.calc = ""
    elif key == "⌫":
        s.calc = s.calc[:-1]
    elif key == "=":
        expr = s.calc.replace("×", "*").replace("÷", "/").replace("−", "-")
        try:
            if not expr or not all(c in "0123456789+-*/.() " for c in expr):
                raise ValueError

            result = eval(expr, {"__builtins__": {}})
            if float(result).is_integer():
                result = int(result)

            s.calc = str(round(result, 8)) if isinstance(result, float) else str(result)
        except Exception:
            s.calc = "Error"
    else:
        if s.calc == "Error":
            s.calc = ""
        s.calc += key


def run():
    st.title("🧮 Calculator")
    if "calc" not in st.session_state:
        st.session_state.calc = ""

    with st.container(key="calculator_pad"):
        st.markdown(
            f"<div style='background:var(--phone-surface); border-radius:15px; padding:20px; "
            f"text-align:right; font-size:34px; min-height:70px; "
            f"border:1px solid var(--phone-line); word-wrap:break-word; margin-bottom:20px;'>"
            f"{st.session_state.calc or '0'}</div>",
            unsafe_allow_html=True,
        )

        rows = [
            ["C", "(", ")", "⌫"],
            ["7", "8", "9", "÷"],
            ["4", "5", "6", "×"],
            ["1", "2", "3", "−"],
            ["0", ".", "=", "+"],
        ]
        for r, row in enumerate(rows):
            cols = st.columns(4)
            for k, key in enumerate(row):
                cols[k].button(
                    key,
                    key=f"k{r}{k}",
                    on_click=press,
                    args=(key,),
                    use_container_width=True,
                )