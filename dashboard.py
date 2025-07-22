import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect
from run import add_univ

st.logo('logo.png')
st.title("Mini iCARE")

# Connect to SQLite
engine = create_engine("sqlite:///univ_database.db")
inspector = inspect(engine)
tables = inspector.get_table_names()

# # Session state to control navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.title("What do you want to do?")
    choice = st.radio("Select an option:", ["Check if university is in database", "Explore tables"])

    if choice == "Check if university is in database":
        st.sidebar.button("⬅ Back to Home", on_click=go_home)
        univ_url = st.text_input("Enter university url:")
        if univ_url:
            if not univ_url.startswith("https://www."):
                univ_url = "https://www." + univ_url
            if not (".ac.uk" in univ_url or ".edu" in univ_url):
                st.error("URL doesn't look like a UK university site (e.g. must contain .ac.uk or .edu)")
            else:
                query = "SELECT 1 FROM universities WHERE home_url = ? LIMIT 1"
                result = pd.read_sql(query, engine, params=(univ_url,))
                if not result.empty:
                    st.success(f"{univ_url} is in the database.")
                else:
                    st.error(f"{univ_url} is NOT in the database.")
                    action = st.radio("Do you want to add it?", ["No", "Yes"])
                    if action == "Yes":
                        st.write("Adding it...")
                        #add_univ(univ_url)
                    else:
                        st.write("❌ Skipped adding the university.")
    elif choice == "Explore tables":
        st.session_state.page = "explore"
        st.rerun()

elif st.session_state.page == "explore":
    st.sidebar.button("⬅ Back to Home", on_click=go_home)
    # table selection
    table = st.sidebar.selectbox("Select a table", tables)
    df = pd.read_sql(f"SELECT * FROM {table}", engine)
    #cols selection
    all_columns = list(df.columns)
    selected_cols = st.sidebar.multiselect("Select columns to display", all_columns, default=all_columns)
    # filter
    col = st.sidebar.selectbox("Filter by", ['None']+selected_cols)
    lim = st.sidebar.number_input("Limit rows", min_value=1, value=100, step=5)
    if col=='None':
        cols_str = ", ".join([f'"{c}"' for c in selected_cols])  
        query = f"SELECT {cols_str} FROM {table} LIMIT {int(lim)}"
        df = pd.read_sql(query, engine)
    else:
        value = st.sidebar.selectbox("With value", df[col].unique())
        cols_str = ", ".join([f'"{c}"' for c in selected_cols]) 
        query = f"SELECT {cols_str} FROM {table} WHERE {col} = ? LIMIT {int(lim)}"
        df = pd.read_sql(query, engine, params=(value,))
    
    st.subheader(f"Table: {table}")
    st.dataframe(df, use_container_width=True)
