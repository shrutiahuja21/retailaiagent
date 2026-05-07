import streamlit as st
import os
from agent import RetailAgent

# Page config
st.set_page_config(page_title="Étoile AI Assistant", page_icon="👗", layout="wide")

# Custom CSS to match the design
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        text-align: left;
        padding-left: 1rem;
    }
    .example-card {
        padding: 1rem;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        margin-bottom: 1rem;
        cursor: pointer;
    }
    .example-title {
        font-weight: bold;
        font-size: 0.9rem;
    }
    .example-subtitle {
        font-size: 0.75rem;
        color: #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for messages and agent
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Étoile AI assistant. I can help you find the perfect outfit or resolve an order issue. What can I do for you today?"}
    ]

if "agent" not in st.session_state:
    st.session_state.agent = RetailAgent()

# Sidebar
with st.sidebar:
    st.title("👗 Étoile AI Assistant")
    st.info("Local Data-Driven Engine Active")
    
    st.subheader("QUICK EXAMPLES")
    
    examples = [
        {"title": "Modest gown under $300, size 8, on sale", "subtitle": "Shopping"},
        {"title": "Show me evening dresses under $200", "subtitle": "Shopping"},
        {"title": "Order O0005 - Can I return this?", "subtitle": "Support"},
        {"title": "What are your bestselling gowns?", "subtitle": "Shopping"},
    ]
    
    for ex in examples:
        if st.button(f"{ex['title']}\n{ex['subtitle']}", key=ex['title']):
            st.session_state.messages.append({"role": "user", "content": ex['title']})
            with st.spinner("Processing..."):
                response = st.session_state.agent.run(ex['title'])
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Main Header
st.markdown("### Intelligent Retail Assistant")

# Chat Container
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = st.session_state.agent.run(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
