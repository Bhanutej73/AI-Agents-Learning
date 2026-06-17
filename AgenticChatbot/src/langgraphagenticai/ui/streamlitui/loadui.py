import streamlit as st
import os

from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config=Config()
        self.user_controls={}

    def load_streamlit_ui(self):
        st.set_page_config(page_title=self.config.get_page_title(), layout="wide")
        st.header(self.config.get_page_title())

        with st.sidebar:
            llm_providers=self.config.get_llm_providers()
            use_case_options=self.config.get_usecase_options()

            self.user_controls["llm_provider"]=st.selectbox("Select LLM Provider", llm_providers)
            self.user_controls["use_case"]=st.selectbox("Select Use Case", use_case_options)
            
            if self.user_controls["llm_provider"]=="Groq":
                model_options=self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"]=st.selectbox("Select Model", model_options)
                self.user_controls["groq_api_key"]=st.text_input("Enter Groq API Key", type="password")

                if not self.user_controls["groq_api_key"]:
                    st.warning("Please enter your Groq API Key to proceed. Don't have one? refer to: https://console.groq.com/keys")

            #self.user_controls["selected_use_case"]=st.selectbox("Select Use Case", use_case_options)
        return self.user_controls