import streamlit as st
import pandas as pd


def explorer_page():
    with st.sidebar:
        st.header("PROJECT1")
        try:
            st.image("landing_pg.png", width=150)
        except Exception:
            st.write("👩‍💻")

        st.header("controls")
        r1 = st.slider("rows to show", 10, 150, key="w_rows")

    st.title("DATA EXPLORER")
    st.caption("upload your csv file")
    files = st.file_uploader("upload your file", type=["csv"])

    if files is not None:
        if st.session_state.get("fname") != files.name:
            for k in list(st.session_state.keys()):
                if k.startswith("w_") and k != "w_rows":
                    del st.session_state[k]
            st.session_state["fname"] = files.name

        d = pd.read_csv(files)
        st.session_state["df"] = pd.DataFrame(d)

    if "df" in st.session_state:
        df = st.session_state["df"]
        st.caption("File loaded ✅")
        rows = df.shape[0]
        cols = df.shape[1]
        missing = int(df.isnull().sum().sum())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("total rows", rows)
        with col2:
            st.metric("total columns", cols)
        with col3:
            st.metric("total missing values", missing)

        st.divider()
        st.dataframe(df.head(r1))

        filter_column = st.selectbox("filter column", df.columns, key="w_filter")
        values = []
        for value in df[filter_column].dropna().unique():
            values.append(value)
        values.sort()

        ckey = f"w_chosen_{filter_column}"
        if ckey not in st.session_state:
            st.session_state[ckey] = values
        chosen = st.multiselect("Choose values", values, key=ckey)
        filtered = df[df[filter_column].isin(chosen)]

        st.dataframe(filtered)
        st.info("charts")
        numeric_cols = filtered.select_dtypes(include="number").columns.tolist()

        if numeric_cols:
            plot_col = st.selectbox("Column to plot", numeric_cols, key="w_plot")
            chart_type = st.radio(
                "Chart type", ["Line", "Bar"], horizontal=True, key="w_chart"
            )

            st.write("Chart")
            if chart_type == "Line":
                st.line_chart(filtered[plot_col])
            else:
                st.bar_chart(filtered[plot_col])
        else:
            st.info("No numeric columns are available to chart.")

        st.download_button(
            "download file",
            df.to_csv(index=False).encode("utf-8"),
            file_name="stream.csv",
            mime="text/csv",
        )
    else:
        st.info("Upload a CSV file to start")


def summary_page():
    st.header("Summary Statistics")

    if "df" in st.session_state:
        st.dataframe(st.session_state["df"].describe())
    else:
        st.info("Upload a CSV on the Explorer tab first.")


def run():
    tab1, tab2 = st.tabs(["📊 Explorer", "📈 Summary"])
    with tab1:
        explorer_page()
    with tab2:
        summary_page()