@echo off
cd %cd%

pip install streamlit requests bs4

streamlit run CNN_Crawl.py

pause
