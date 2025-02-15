# -*- coding: utf-8 -*-
"""AI_project_Hugging_Face.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X9omJG898EVC2uQj0VDkEaTbopS-tTUX

**Install Python libraries for NLP and machine learning**
"""

!pip install transformers datasets torch pandas

"""**Load Microsoft's DialoGPT-small model for conversational AI and using tokenizer**"""

!pip install langchain-community # Install langchain-community package
from langchain.llms import HuggingFacePipeline # Import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline # Import the pipeline function

# Load the small conversational model
model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Create an LLM pipeline for LangChain
chatbot_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=200)
llm = HuggingFacePipeline(pipeline=chatbot_pipeline)

"""**Trial to Streamlit**"""

import pandas as pd
import streamlit as st

# Convert JSON to DataFrame for fast filtering
df_catalog = pd.DataFrame(product_catalog)

def find_products(query):
    """Filter products based on user queries."""
    query_lower = query.lower()

    # Extract price condition
    price_limit = None
    if "under $" in query_lower:
        try:
            price_limit = int(query_lower.split("under $")[1].split()[0])
        except ValueError:
            pass

    # Extract category
    category = None
    for cat in df_catalog["category"].unique():
        if cat in query_lower:
            category = cat

    # Filter products
    filtered = df_catalog[
        (df_catalog["price"] <= price_limit if price_limit else True) &
        (df_catalog["category"] == category if category else True) &
        (df_catalog["stock"] > 0)
    ]

    return filtered.head(3)  # Return top 3 results

# Test filtering
print(find_products("Find me electronics under $50"))

# Streamlit UI code
st.title("Product Search App")
st.write("Enter a search query (e.g., 'Find me electronics under $50') and get results!")

query = st.text_input("Enter your search query:", "")

if st.button("Search"):
    if query:
        results = find_products(query)
        if not results.empty:
            st.write(f"### Results for: **{query}**")
            st.dataframe(results)  # Display results in a table
        else:
            st.warning("No matching products found!")
    else:
        st.warning("Please enter a search query.")

"""**Generate a Scalable Product Catalog and save to json file**"""

import random
import json

# Sample categories, brands, and attributes
categories = ["Electronics", "Furniture", "Stationery", "Clothing", "Accessories", "Home Appliances", "Laptops"]
brands = ["Apple", "Samsung", "Sony", "LG", "HP", "Dell", "IKEA", "Nike", "Adidas"]
delivery_times = ["Same-day", "Next-day", "2-3 days", "1 week"]

# Generate an enhanced product catalog
def generate_product_catalog(num_items):
    catalog = []
    for i in range(1, num_items + 1):
        product = {
            "id": i,
            "name": f"Product {i}",
            "brand": random.choice(brands),
            "price": round(random.uniform(5, 2000), 2),
            "category": random.choice(categories),
            "stock": random.randint(0, 200),
            "rating": round(random.uniform(1, 5), 1),  # Ratings between 1.0 and 5.0
            "discount": random.randint(0, 50),         # Discount percentage
            "delivery_time": random.choice(delivery_times),
        }
        catalog.append(product)
    return catalog




# Convert to DataFrame
product_catalog = generate_product_catalog(1000)
print(f"Catalog size: {len(product_catalog)} items")

# Save the catalog to a JSON file for reuse
with open("product_catalog.json", "w") as f:
    json.dump(product_catalog, f, indent=4)

"""**Complex Query Handling**"""

import pandas as pd
!pip install langchain
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
print(find_products("Find me Apple laptops under $1000"))
#print(find_products("Find me Sony TVs  delivered on Same-day and under $500"))
#print(find_products("Find me Sony TVs that will be delivered on Same-day and under $500"))
#print(find_products("Find me Furniture with at least 20% off"))
#print(find_products("Find me Electronics rated above 4 stars"))
#print(find_products("Find me Sony TVs under $500 rated above 4.5 stars with at least 30% off"))
#print(find_products("Find me Apple laptops under $1000 rated above 4 stars with at least 20% off"))

"""**Version 1 for prompt chatbot**"""

# Define a prompt template
prompt = PromptTemplate(
    input_variables=["query"],
    template="I am a helpful shopping assistant.\n{query}"
)

# Create LangChain LLMChain
chain = LLMChain(llm=llm, prompt=prompt)

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

# Global variable to store the last searched products
filtered_products = pd.DataFrame()  # Empty DataFrame at the start

def chat_with_bot(user_query):
    """Handles user queries with chatbot and product recommendations."""
    global filtered_products  # Access the global variable
    query_type = classify_query(user_query)

    if query_type == "product_search":
        # Search for products
        filtered_products = find_products(user_query)

        if not filtered_products.empty:
            product_list = "\n".join([f"{row['name']} - ${row['price'] } - {row['category'] } - {row['brand'] } -  {row['rating'] } - {row['discount'] }" for _, row in filtered_products.iterrows()])
            response_text = f"Here are some options:\n{product_list}"
        else:
            response_text = "Sorry, no matching products found."

    elif query_type == "availability_check":
        if not filtered_products.empty:
            in_stock = [f"Checking stock for: {row['name']} - Stock: {row['stock']}" for _, row in filtered_products.iterrows() if row["stock"] > 0]
            response_text = "\n".join(in_stock) if in_stock else "None of these items are currently in stock."

        else:
            response_text = "Please search for a product first."

    elif query_type == "delivery_check":
        #if 'filtered_products' in locals() and not filtered_products.empty:
        if not filtered_products.empty:
            fast_delivery = [row["name"] for _, row in filtered_products.iterrows() if row["delivery_time"] == "Next Day" or row["delivery_time"] == "Same-day"]
            response_text = f"These items can be delivered today or tomorrow maximum: {', '.join(fast_delivery)}" if fast_delivery else "None of these items can be delivered today or tomorrow."
        else:
            response_text = "Please search for a product first."

    else:
        response_text = "I'm here to help! You can ask me to find products, check availability, or delivery options."

    # Generate chatbot response
    chatbot_reply = chain.run(response_text)

    return chatbot_reply

############################################## Test chatbot################################################################
exit_words = {"thank you", "bye", "exit", "quit","thanks", "thanks!", "thanks alot", "ok"}

while True:
    inquiry = input("Enter your inquiry:  ").strip().lower()
    if inquiry in exit_words:
        print("Any time. Goodbye!")
        break
    print(chat_with_bot(inquiry))

#Samples of questions:

#Group 1 questions:
#print(chat_with_bot("Hi"))
#print(chat_with_bot("Show me Apple Laptops under $500"))
#print(chat_with_bot("Can these be delivered tomorrow?"))

#Group 2 questions:
#print(chat_with_bot("I want to ask about something"))
#print(find_products("I need Sony Accessories under $500"))
#print(chat_with_bot("How many items are available?"))

#Group 3 questions:
#print(find_products("Find me Furniture with at least 20% off"))
#print(chat_with_bot("Are these in stock?"))
#print(chat_with_bot("ok, thank you"))
#print(chat_with_bot("thank you"))

#Group 4 questions:
#print(chat_with_bot("Good evening!"))
#print(find_products("Find me Sony Laptops under $500 rated above 4.5 stars with at least 30% off"))
#print(chat_with_bot("Are these in stock?"))
#print(chat_with_bot("Can these be delivered today?"))
#print(chat_with_bot("I have another inqury"))
#print(find_products("Find me Electronics rated above 4 stars"))
#print(chat_with_bot("How many items are in stock?"))
#print(chat_with_bot("thanks"))

#Group 5 questions:
#print(chat_with_bot("Are these in stock?"))
#print(chat_with_bot("ok"))

"""**Modified version 2 for prompt chatbot**"""

import os  # Import os to check file existence

# File to save filtered products
filtered_products_file = "filtered_products.csv"

# Load last saved filtered products if file exists
if os.path.exists(filtered_products_file):
    filtered_products = pd.read_csv(filtered_products_file)
else:
    filtered_products = pd.DataFrame()  # Start with an empty DataFrame



# Define a prompt template
prompt = PromptTemplate(
    input_variables=["query"],
    template="I am a helpful shopping assistant.\n{query}"
)


# Create LangChain LLMChain
chain = LLMChain(llm=llm, prompt=prompt)

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
    global filtered_products  # Access the global variable
    query_type = classify_query(user_query)

    if query_type == "product_search":
        # Search for products
        filtered_products = find_products(user_query)

        if not filtered_products.empty:
            product_list = "\n".join([f"{row['name']} - ${row['price']} - {row['category']} - {row['brand']} - {row['rating']} - {row['discount']}" for _, row in filtered_products.iterrows()])
            response_text = f"Here are some options:\n{product_list}"
            # Save filtered products to CSV
            filtered_products.to_csv(filtered_products_file, index=False)
        else:
            response_text = "Sorry, no matching products found."

    elif query_type == "availability_check":
        if not filtered_products.empty:
            in_stock = [f"Checking stock for: {row['name']} - Stock: {row['stock']}" for _, row in filtered_products.iterrows() if row["stock"] > 0]
            response_text = "\n".join(in_stock) if in_stock else "None of these items are currently in stock."
        else:
            response_text = "Please search for a product first."

    elif query_type == "delivery_check":
        if not filtered_products.empty:
            fast_delivery = [row["name"] for _, row in filtered_products.iterrows() if row["delivery_time"] == "Next Day" or row["delivery_time"] == "Same-day"]
            response_text = f"These items can be delivered today or tomorrow maximum: {', '.join(fast_delivery)}" if fast_delivery else "None of these items can be delivered today or tomorrow."
        else:
            response_text = "Please search for a product first."

    else:
        response_text = "I'm here to help! You can ask me to find products, check availability, or delivery options."

    # Generate chatbot response
    chatbot_reply = chain.run(response_text)

    return chatbot_reply

############################################## Test chatbot################################################################
exit_words = {"thank you", "bye", "exit", "quit","thanks", "thanks!", "thanks alot", "ok"}

while True:
    inquiry = input("Enter your inquiry:  ").strip().lower()
    if inquiry in exit_words:
        print("Any time. Goodbye!")
        break
    print(chat_with_bot(inquiry))

#Samples of questions:

#Group 1 questions:
#print(chat_with_bot("Hi"))
#print(chat_with_bot("Show me Apple Laptops under $500"))
#print(chat_with_bot("Can these be delivered tomorrow?"))

#Group 2 questions:
#print(chat_with_bot("I want to ask about something"))
#print(find_products("I need Sony Accessories under $500"))
#print(chat_with_bot("How many items are available?"))

#Group 3 questions:
#print(find_products("Find me Furniture with at least 20% off"))
#print(chat_with_bot("Are these in stock?"))
#print(chat_with_bot("ok, thank you"))
#print(chat_with_bot("thank you"))

#Group 4 questions:
#print(chat_with_bot("Good evening!"))
#print(find_products("Find me Sony Laptops under $500 rated above 4.5 stars with at least 30% off"))
#print(chat_with_bot("Are these in stock?"))
#print(chat_with_bot("Can these be delivered today?"))
#print(chat_with_bot("I have another inqury"))
#print(find_products("Find me Electronics rated above 4 stars"))
#print(chat_with_bot("How many items are in stock?"))
#print(chat_with_bot("thanks"))

#Group 5 questions:
#print(chat_with_bot("Are these in stock?"))
#print(chat_with_bot("ok"))

"""**Connecting to streamlit**"""

!pip install streamlit
import streamlit as st
import requests


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
if not os.path.exists(json_path):
    st.error(f"ERROR: The JSON file '{json_path}' is missing.")
    st.stop()
df_catalog = pd.read_json(json_path)

# ✅ Debug: Print loaded JSON data
st.write("✅ Loaded Product Catalog:", df_catalog.head())

# ✅ Hugging Face API Key (Set it in Streamlit Secrets)
HUGGINGFACE_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]

# ✅ Choose a Free Model (LLM)
#MODEL_NAME = "tiiuae/falcon-7b-instruct"
MODEL_NAME = "microsoft/DialoGPT-small"
#chatfunction
def chat_with_bot(user_query):
    """Handles user queries with chatbot and product recommendations."""
    global filtered_products  # Access the global variable
    query_type = classify_query(user_query)

    if query_type == "product_search":
        # Search for products
        filtered_products = find_products(user_query)

        if not filtered_products.empty:
            product_list = "\n".join([f"{row['name']} - ${row['price'] } - {row['category'] } - {row['brand'] } -  {row['rating'] } - {row['discount'] }" for _, row in filtered_products.iterrows()])
            response_text = f"Here are some options:\n{product_list}"
        else:
            response_text = "Sorry, no matching products found."

    elif query_type == "availability_check":
        if not filtered_products.empty:
            in_stock = [f"Checking stock for: {row['name']} - Stock: {row['stock']}" for _, row in filtered_products.iterrows() if row["stock"] > 0]
            response_text = "\n".join(in_stock) if in_stock else "None of these items are currently in stock."

        else:
            response_text = "Please search for a product first."

    elif query_type == "delivery_check":
        #if 'filtered_products' in locals() and not filtered_products.empty:
        if not filtered_products.empty:
            fast_delivery = [row["name"] for _, row in filtered_products.iterrows() if row["delivery_time"] == "Next Day" or row["delivery_time"] == "Same-day"]
            response_text = f"These items can be delivered today or tomorrow maximum: {', '.join(fast_delivery)}" if fast_delivery else "None of these items can be delivered today or tomorrow."
        else:
            response_text = "Please search for a product first."

    else:
        response_text = "I'm here to help! You can ask me to find products, check availability, or delivery options."


    # ✅ Generate AI response
    response_text = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
        headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
        json={"inputs": user_query, "max_new_tokens": 200}  # Limit response length
    )

    if response_text.status_code == 200:
        return response_text.json()[0]["generated_text"]
    else:
        return f"AI Error: {response_text.json()}"


# ✅ Streamlit Chat Interface
st.subheader("Chat with your AI Assistant")
user_query = st.text_input("Ask me anything about our products:")

if st.button("Send"):
    if user_query:
        response = chat_with_bot(user_query)
        st.write(f"*AI:* {response}")

# ✅ Display Chat History
st.subheader("Chat History")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
for msg in st.session_state.chat_history:
    st.write(msg)

!pip install streamlit
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
if not os.path.exists(json_path):
    st.error(f"ERROR: The JSON file '{json_path}' is missing.")
    st.stop()
df_catalog = pd.read_json(json_path)

# ✅ Debug: Print loaded JSON data
st.write("✅ Loaded Product Catalog:", df_catalog.head())

# ✅ Choose a Free Model (LLM)
MODEL_NAME = "microsoft/DialoGPT-small"

# ✅ Initialize global variable
filtered_products = pd.DataFrame()

# ✅ Chatbot Function
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
        f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
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

