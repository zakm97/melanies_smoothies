import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in custom Smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()

# Fruits disponibles avec la colonne SEARCH_ON
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convertit le Snowpark DataFrame en Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Liste des fruits pour le multiselect
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Nom de la commande
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# Choix des fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Récupère la valeur de recherche dans la colonne SEARCH_ON
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        st.subheader(fruit_chosen + " Nutrition Information")

        # Encode les espaces / caractères spéciaux pour l'URL
        search_on_encoded = quote(search_on)

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on_encoded}"
        )

        if smoothiefroot_response.status_code == 200:
            fruit_api_df = pd.json_normalize(smoothiefroot_response.json())
            st.dataframe(fruit_api_df, use_container_width=True)
        else:
            st.warning(f"No data found for {fruit_chosen}")

    if st.button("Submit Order"):
        my_insert_stmt = f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES ('{ingredients_string.replace("'", "''")}', '{name_on_order.replace("'", "''")}')
        """
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon=":material/thumb_up:")
