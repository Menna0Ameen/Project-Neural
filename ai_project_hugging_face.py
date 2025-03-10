# -*- coding: utf-8 -*-
"""AI_project_Hugging_Face.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X9omJG898EVC2uQj0VDkEaTbopS-tTUX

**Install Python libraries for NLP and machine learning**
"""

#!pip install transformers datasets torch pandas

"""**Load Microsoft's DialoGPT-small model for conversational AI and using tokenizer**"""

#!pip install langchain-community # Install langchain-community package
from langchain.llms import HuggingFacePipeline # Import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline # Import the pipeline function

# Load the small conversational model
#model_name = "microsoft/DialoGPT-small"
model_name = "tiiuae/falcon-7b-instruct"
#MODEL_NAME = "tiiuae/falcon-7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Create an LLM pipeline for LangChain
chatbot_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=200)
llm = HuggingFacePipeline(pipeline=chatbot_pipeline)


"""**Generate a Scalable Product Catalog and save to json file**"""

import random
import json


"""**Complex Query Handling**"""

import pandas as pd
#!pip install langchain
from langchain import PromptTemplate, LLMChain # Import PromptTemplate and LLMChain


# Load JSON file into a DataFrame
df_catalog = pd.read_json("product_catalog.json")

# Function to filter products based on user queries
def find_products(query):
    """Filter products based on price, category, delivery_time, brand, rating, and discount."""
    query_lower = query.lower()

    # Extract price condition (e.g., "under $500")   ###
    price_limit = None
    if "under $" in query_lower:
        try:
            price_limit = int(query_lower.split("under $")[1].split()[0])
        except ValueError:
            pass

    # Extract category
    category = None
    for cat in df_catalog["category"].unique():
        if cat.lower() in query_lower:
            category = cat

    # Extract delivery_time
    delivery_time = None
    for d in df_catalog["delivery_time"].unique():
        if d.lower() in query_lower:
            delivery_time = d

    # Extract brand
    brand = None
    for b in df_catalog["brand"].unique():
        if b.lower() in query_lower:
            brand = b

    # Extract rating condition (e.g., "above 4 stars")
    min_rating = None
    if "rated above" in query_lower:
        try:
            min_rating = float(query_lower.split("rated above ")[1].split()[0])
        except ValueError:
            pass

    # Extract discount condition (e.g., "at least 20% off")
    min_discount = None
    if "at least" in query_lower and "%" in query_lower:
        try:
            min_discount = int(query_lower.split("at least ")[1].split("%")[0])
        except ValueError:
            pass

    # Apply filters
    filtered = df_catalog[
        (df_catalog["price"] <= price_limit if price_limit else True) &  #if None so no filter is based on this section
        (df_catalog["category"] == category if category else True) &
        (df_catalog["delivery_time"] == delivery_time if delivery_time else True) &
        (df_catalog["brand"] == brand if brand else True) &
        (df_catalog["rating"] >= min_rating if min_rating else True) &
        (df_catalog["discount"] >= min_discount if min_discount else True) &
        (df_catalog["stock"] > 0)  # Ensure in-stock items   #Ensures only in-stock items are included in the results. This condition is always applied.
    ]

    return filtered.head(5)  # Return top 5 results

# Test the new function with multiple conditions:
#print(find_products("Find me Apple laptops under $1000"))
#print(find_products("Find me Sony TVs  delivered on Same-day and under $500"))
#print(find_products("Find me Sony TVs that will be delivered on Same-day and under $500"))
#print(find_products("Find me Furniture with at least 20% off"))
#print(find_products("Find me Electronics rated above 4 stars"))
#print(find_products("Find me Sony TVs under $500 rated above 4.5 stars with at least 30% off"))
#print(find_products("Find me Apple laptops under $1000 rated above 4 stars with at least 20% off"))



"""**Connecting to streamlit**"""



#!pip install streamlit
import os
import streamlit as st
import requests
import pandas as pd

# ✅ Streamlit App Title
st.title("🛒 AI-Powered E-Commerce Chatbot (Free Version)")

# ✅ Check if the API key is available in secrets
if "HUGGINGFACE_API_KEY" in st.secrets:
    HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
else:
    st.error("🚨 Hugging Face API Key is missing! Add it in Streamlit Secrets.")
    st.stop()

# ✅ Load Product Catalog
json_path = "product_catalog.json"
#if not os.path.exists(json_path):
 #   st.error(f"ERROR: The JSON file '{json_path}' is missing.")
  #  st.stop()
#df_catalog = pd.read_json(json_path)

# ✅ Debug: Print loaded JSON data
#st.write("✅ Loaded Product Catalog:", df_catalog.head())

# ✅ Choose a Free Model (LLM)
#MODEL_NAME = "microsoft/DialoGPT-small"

# ✅ Initialize global variable
filtered_products = pd.DataFrame()

# ✅ Chatbot Function
def classify_query(user_query):
    """Classifies the query type based on keywords."""
    user_query = user_query.lower()

    if any(word in user_query for word in ["find", "show", "recommend", "under", "cheapest", "I need"]):
        return "product_search"
    elif any(word in user_query for word in ["stock", "available", "in stock","in-stock"]):
        return "availability_check"
    elif any(word in user_query for word in ["deliver", "shipping", "arrive"]):
        return "delivery_check"
    else:
        return "general"
        
def chat_with_bot(user_query):
    """Handles user queries with chatbot and product recommendations."""
    global filtered_products
    query_type = classify_query(user_query)

    if query_type == "product_search":
        filtered_products = find_products(user_query)

        if not filtered_products.empty:
            product_list = "\n".join([
                f"{row['name']} - ${row['price']} - {row['category']} - {row['brand']} - {row['rating']} - {row['discount']}"
                for _, row in filtered_products.iterrows()
            ])
            response_text = f"Here are some options:\n{product_list}"
        else:
            response_text = "Sorry, no matching products found."

    elif query_type == "availability_check":
        if not filtered_products.empty:
            in_stock = [
                f"Checking stock for: {row['name']} - Stock: {row['stock']}"
                for _, row in filtered_products.iterrows() if row["stock"] > 0
            ]
            response_text = "\n".join(in_stock) if in_stock else "None of these items are currently in stock."
        else:
            response_text = "Please search for a product first."

    elif query_type == "delivery_check":
        if not filtered_products.empty:
            fast_delivery = [
                row["name"] for _, row in filtered_products.iterrows()
                if row["delivery_time"] in ["Next Day", "Same-day"]
            ]
            response_text = f"These items can be delivered today or tomorrow: {', '.join(fast_delivery)}" if fast_delivery else "None of these items can be delivered today or tomorrow."
        else:
            response_text = "Please search for a product first."

    else:
        response_text = "I'm here to help! You can ask me to find products, check availability, or delivery options."

    # ✅ AI Response via Hugging Face API
    response_text = requests.post(
        f"https://api-inference.huggingface.co/models/{model_name}",
        headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
        json={"inputs": user_query, "max_new_tokens": 200}
    )

    response_data = response_text.json()
    if response_text.status_code == 200 and response_data:
        return response_data[0].get("generated_text", "No response generated.")
    else:
        return f"AI Error: {response_data}"

# ✅ Streamlit Chat Interface
st.subheader("Chat with your AI Assistant")
user_query = st.text_input("Ask me anything about our products:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Send"):
    if user_query:
        response = chat_with_bot(user_query)
        st.session_state.chat_history.append(f"**You:** {user_query}")
        st.session_state.chat_history.append(f"**AI:** {response}")
        st.write(f"*AI:* {response}")

# ✅ Display Chat History
st.subheader("Chat History")
for msg in st.session_state.chat_history:
    st.write(msg)

