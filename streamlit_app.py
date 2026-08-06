import streamlit as st
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in custom Smoothie!")


cnx = st.connection("snowflake")
session = cnx.session()

# Fruits disponibles
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
fruit_names = [row["FRUIT_NAME"] for row in fruit_df.select("FRUIT_NAME").collect()]

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

if ingredients_list and name_on_order:
    ingredients_string = " ".join(ingredients_list)
    st.write("Your selected ingredients:", ingredients_string)

    if st.button("Submit Order"):
        my_insert_stmt = f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            VALUES ('{ingredients_string.replace("'", "''")}', '{name_on_order.replace("'", "''")}')
        """
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon=":material/thumb_up:")

import requests  
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())


sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width = True)
