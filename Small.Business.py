import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config(page_title= "Grocery Store Application",
                   page_icon = "🍎",
                   layout="centered",
                   initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "role" not in st.session_state:
    st.session_state["role"] = None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "messages" not in st.session_state:
    st.session_state["messages"]= [
        
        {
            "role": "assistant",
            "content": "Hi! How can I help you?"
        }
    ]

if not st.session_state["logged_in"]:
    st.session_state["page"] = "home"

json_path_inventory = Path("inventory.json")
json_path_orders = Path("order.json")

inventory = []
orders = []

if json_path_inventory.exists():
    with open(json_path_inventory, "r") as f:
        inventory = json.load(f)

if json_path_orders.exists():
    with open(json_path_orders, "r") as f:
        orders = json.load(f)

def go(page_name):
    st.session_state["page"] = page_name
    st.rerun()

def logout():
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["page"] = "home"
    st.rerun()

with st.sidebar:

    st.title("Navigation")

    if st.button("Home"):
        go("home")

    if st.session_state["logged_in"]:

        if st.session_state["role"] == "user":
            if st.button("Orders"):
                go("orders")

        if st.session_state["role"] == "employee":
            if st.button("Inventory"):
                go("inventory")

        st.divider()

        if st.button("Log out"):
            logout()

if st.session_state["page"] == "home":

    if st.session_state["logged_in"]:
        if st.session_state["role"] == "employee":
            go("inventory")
        else:
            go("orders")
        st.stop()

    st.markdown("# 🍎 New London Grocery Store")
    st.markdown("Welcome! Please login or create an account below.")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):

            st.subheader("Login")

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                role_guess = st.selectbox("Login as", ["user", "employee"])

                submitted = st.form_submit_button("Login")

            if submitted:

                if username and password:

                    # set session state
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = role_guess

                    # ROLE-BASED REDIRECT
                    if role_guess == "employee":
                        go("inventory")
                    else:
                        go("orders")

                else:
                    st.error("Please enter both username and password")

    # =========================
    # REGISTER BOX
    # =========================
    with col2:
        with st.container(border=True):

            st.subheader("Register")

            with st.form("register_form", clear_on_submit=True):
                email = st.text_input("Email")
                name = st.text_input("Full Name")
                password = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["user", "employee"])

                created = st.form_submit_button("Create Account")

            if created:
                with st.spinner("Creating account..."):
                    time.sleep(1)

                st.success("Account created! Please login.")

elif st.session_state["page"] == "inventory":
    if st.session_state["role"] != "employee":
        st.error("Access denied.")
        st.stop()
    st.markdown("# 📦 Inventory Dashboard")

    col1, col2, col3 = st.columns([3, 3, 3])

    with col1:
        selected_category = st.radio(
            "Select a List",
            ["Inventory", "Orders"],
            horizontal=True
        )
        if selected_category == "Inventory":
            if inventory:
                st.dataframe(inventory)
            else:
                st.warning("No items in inventory")
        else:
            if orders:
                st.dataframe(orders)
            else:
                st.warning("No orders yet")

    with col2:
        if selected_category == "Inventory":
            st.metric("Total Inventory Items", len(inventory))
        else:
            st.metric("Total Orders", len(orders))

elif st.session_state["page"] == "orders":

    if st.session_state["role"] != "user":
        st.error("Access denied.")
        st.stop()

    st.markdown("# 🛒 Orders")

    tab1, tab2 = st.tabs(["Add New Order", "Cancel Order"])

    with tab1:
            col1, col2 = st.columns([3, 3])

            with col1: 
                st.subheader("Add New Order")

                if inventory: 
                    selected_item= st.selectbox("Items",options=inventory,
                                        format_func= lambda x: f"{x["name"]}")

                    quantity = st.number_input("Quantity",min_value=1, step=1)

                    if st.button("Create Order", key="create_order_btn",type="primary",use_container_width=True):
                        with st.spinner("Creating the order ... "):
                            total= quantity * selected_item["price"]
                            for item in inventory:
                                if item["id"]==selected_item["id"]:
                                    item["stock"]=item["stock"]- quantity 
                                    break

                            orders.append(
                                {
                                    "id": str(uuid.uuid4()),
                                    "item_id": selected_item["id"],
                                    "item_name": selected_item["name"],
                                    "quantity": quantity,
                                    "status": "active",   # 👈 important
                                    "total": total,
                                    "timestamp": str(datetime.now())
                                }
                            )
                            
                        with open(json_path_inventory,"w") as f:
                            json.dump(inventory,f)

                        with open(json_path_orders, "w") as f:
                            json.dump(orders,f)

                        st.success("Order created!")
                        st.balloons()

                        time.sleep(5)
                        st.session_state["page"] = "home"
    with col2:
        st.subheader("Chatbot - AI Assistant")
        col11,col22=st.columns([2,2])
        with col11:
            st.caption("Try Asking: How Can I Add a New Order?")
        with col2:
            if st.button("Clear", key="clear_chat_btn"):
                if "messages" not in st.session_state:
                    st.session_state["messages"]= [
                         {
            "role": "assistant",
            "content": "Hi! How can I help you?"
                        }
            ]

        with st.container(border=True, height=250):
            for message in st.session_state["messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        user_input = st.chat_input("Ask a question...")
        if user_input:
            with st.spinner("Thinking..."):
                st.session_state["messages"].append(
                    {
                        "role": "user",
                        "content": user_input
                    }
                )

                ai_response="I could not find an answer for it, try again!"

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": ai_response 
                    }
                )
    with tab2: 
        st.subheader("Cancel Order") 
        active_orders = [o for o in orders if o["status"] == "active"]

        if not active_orders:
            st.info("No active orders to cancel.")
        else:

            selected_order = st.selectbox(
                "Select order to cancel",
                options=active_orders,
                format_func=lambda x: f"{x['item_name']} | Qty: {x['quantity']} | Total: ${x['total']}"
            )

            if st.button("Cancel Order", type="primary"):
                
                for order in orders:
                    if order["id"] == selected_order["id"]:
                        order["status"] = "cancelled"

                for item in inventory:
                    if item["id"] == selected_order["item_id"]:
                        item["stock"] += selected_order["quantity"]
                        break

                with open(json_path_orders, "w") as f:
                    json.dump(orders, f)

                with open(json_path_inventory, "w") as f:
                    json.dump(inventory, f)

                st.success("Order cancelled successfully!")
                st.rerun()
