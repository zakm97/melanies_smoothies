import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()

# Fruits disponibles
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
fruit_names = [row["FRUIT_NAME"] for row in fruit_df.select("FRUIT_NAME").collect()]

# Correspondance entre les noms de la BDD et ceux de l'API
fruit_api_names = {
    "Apples": "apple",
    "Blueberries": "blueberry",
    "Elderberries": "elderberry",
    "Figs": "fig",
    "Raspberries": "raspberry",
    "Strawberries": "strawberry"
}

# Nom sur la commande
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

    ingredients_string = " ".join(ingredients_list)

    st.write("Your selected ingredients:", ingredients_string)

    # Pour chaque fruit sélectionné
    for fruit_chosen in ingredients_list:

        fruit_url = fruit_api_names.get(
            fruit_chosen,
            fruit_chosen.lower()
        )

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_url}"
        )

        st.subheader(fruit_chosen)

        if smoothiefroot_response.status_code == 200:
            st.dataframe(
                smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.warning(f"No information found for {fruit_chosen}")

    if st.button("Submit Order"):

        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (INGREDIENTS, NAME_ON_ORDER)
        VALUES
            ('{ingredients_string.replace("'", "''")}',
             '{name_on_order.replace("'", "''")}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon=":material/thumb_up:"
        )
