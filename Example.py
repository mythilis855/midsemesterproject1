import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Grocery Store Application",
    page_icon="🍎",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "role" not in st.session_state:
    st.session_state["role"] = None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ---------------- FILE PATHS ----------------
json_path_inventory = Path("inventory.json")
json_path_orders = Path("orders.json")
json_path_users = Path("users.json")

# ---------------- LOAD DATA ----------------
def load_data(path):
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_data(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except:
        st.error("Error saving data")

inventory = load_data(json_path_inventory)
orders = load_data(json_path_orders)
users = load_data(json_path_users)

# ---------------- NAVIGATION ----------------
with st.sidebar:
    st.title("Navigation")

    if st.button("Home", key="nav_home"):
        st.session_state["page"] = "home"
        st.rerun()

    if st.session_state["logged_in"]:
        if st.session_state["role"] == "user":
            if st.button("Orders", key="nav_orders"):
                st.session_state["page"] = "orders"
                st.rerun()

        if st.session_state["role"] == "employee":
            if st.button("Inventory", key="nav_inventory"):
                st.session_state["page"] = "inventory"
                st.rerun()

        st.divider()

        if st.button("Logout", key="nav_logout"):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.session_state["page"] = "home"
            st.rerun()

# ---------------- HOME ----------------
if st.session_state["page"] == "home":

    if st.session_state["logged_in"]:
        st.session_state["page"] = (
            "inventory" if st.session_state["role"] == "employee" else "orders"
        )
        st.rerun()

    st.title("🍎 New London Grocery Store")
    st.write("Login or create an account")

    col1, col2 = st.columns(2)

    # ---------- REGISTER ----------
    with col1:
        st.subheader("Register")

        with st.form("register_form"):
            email = st.text_input("Email")
            name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "employee"])

            if st.form_submit_button("Create Account"):
                if not email or not name or not username or not password:
                    st.error("All fields required")
                elif any(u["email"] == email for u in users):
                    st.error("Email already exists")
                elif any(u["username"] == username for u in users):
                    st.error("Username taken")
                else:
                    users.append({
                        "email": email,
                        "name": name,
                        "username": username,
                        "password": password,
                        "role": role
                    })
                    save_data(json_path_users, users)
                    st.success("Account created!")

    # ---------- LOGIN ----------
    with col2:
        st.subheader("Login")

        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            role_guess = st.selectbox("Login as", ["user", "employee"])

            if st.form_submit_button("Login"):
                if not username or not password:
                    st.error("Enter username and password")
                else:
                    user = next((u for u in users if u["username"] == username), None)

                    if not user:
                        st.error("User not found")
                    elif user["password"] != password:
                        st.error("Wrong password")
                    elif user["role"] != role_guess:
                        st.error("Wrong role")
                    else:
                        st.session_state["logged_in"] = True
                        st.session_state["role"] = user["role"]
                        st.session_state["page"] = (
                            "inventory" if user["role"] == "employee" else "orders"
                        )
                        st.rerun()

# ---------------- INVENTORY ----------------
elif st.session_state["page"] == "inventory":

    if st.session_state["role"] != "employee":
        st.error("Access denied")
        st.stop()

    st.title("📦 Inventory Dashboard")

    st.metric("Total Items", len(inventory))
    st.divider()

    if not inventory:
        st.warning("No inventory items")
    else:
        for item in inventory:
            with st.container(border=True):
                st.subheader(item["name"])
                st.write(f"Price: ${item['price']}")
                st.write(f"Stock: {item['stock']}")

# ---------------- ORDERS ----------------
elif st.session_state["page"] == "orders":

    if st.session_state["role"] != "user":
        st.error("Access denied")
        st.stop()

    st.title("🛒 Orders")

    tab1, tab2 = st.tabs(["Create Order", "Cancel Order"])

    # ---------- CREATE ORDER ----------
    with tab1:
        if not inventory:
            st.warning("No items available")
        else:
            selected_item = st.selectbox(
                "Select Item",
                inventory,
                format_func=lambda x: x["name"],
                key="item_select"
            )

            quantity = st.number_input("Quantity", min_value=1, key="qty")

            if st.button("Place Order", key="place_order"):
                total = quantity * selected_item["price"]

                # update stock
                for item in inventory:
                    if item["id"] == selected_item["id"]:
                        item["stock"] -= quantity

                new_order = {
                    "id": str(uuid.uuid4()),
                    "item_id": selected_item["id"],
                    "item_name": selected_item["name"],
                    "quantity": quantity,
                    "total": total,
                    "status": "active",
                    "timestamp": str(datetime.now())
                }

                orders.append(new_order)

                save_data(json_path_orders, orders)
                save_data(json_path_inventory, inventory)

                st.success("Order placed!")
                st.rerun()

    # ---------- CANCEL ORDER ----------
    with tab2:
        active_orders = [o for o in orders if o["status"] == "active"]

        if not active_orders:
            st.info("No active orders")
        else:
            selected_order = st.selectbox(
                "Select Order",
                active_orders,
                format_func=lambda x: f"{x['item_name']} (Qty: {x['quantity']})",
                key="cancel_order"
            )

            if st.button("Cancel Order", key="cancel_btn"):
                for order in orders:
                    if order["id"] == selected_order["id"]:
                        order["status"] = "cancelled"

                for item in inventory:
                    if item["id"] == selected_order["item_id"]:
                        item["stock"] += selected_order["quantity"]

                save_data(json_path_orders, orders)
                save_data(json_path_inventory, inventory)

                st.success("Order cancelled")
                st.rerun()