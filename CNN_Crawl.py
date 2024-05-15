import streamlit as st
import requests
from bs4 import BeautifulSoup

# Helper function to handle requests
def get_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception for HTTP errors
    return response

def fetch_news(url):
    response = get_url(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Dictionary to store data
    news_data = {}

    # Find category headers
    headers = soup.find_all("a", attrs={"data-zjs-navigation-location": "header"})[:13]

    for header in headers:
        category_name = header.text.strip()
        news_data[category_name] = []

        # Get the correct URL
        new_url = header['href']
        if not new_url.startswith('http'):
            new_url = requests.compat.urljoin(url, new_url)

        page_response = get_url(new_url)
        category_soup = BeautifulSoup(page_response.text, "html.parser")

        # Find headlines and URLs
        headlines = category_soup.find_all("span", class_="container__headline-text", attrs={"data-editable": "headline"})
        for headline in headlines:
            parent_link = headline.find_parent("a", href=True)
            if parent_link:
                news_title = headline.get_text(strip=True)
                news_url = parent_link['href']
                if not news_url.startswith('http'):
                    news_url = requests.compat.urljoin(new_url, news_url)

                news_data[category_name].append((news_title, news_url))

    return news_data

# Streamlit application starts here
st.title('CNN News Scraper')

url = "https://edition.cnn.com/"

# Check if news data is already in session state
if 'news_data' not in st.session_state:
    st.session_state.news_data = fetch_news(url)

news_data = st.session_state.news_data

category = st.sidebar.selectbox('Choose a news category:', list(news_data.keys()))
news_count = st.sidebar.number_input('Select the number of news items to display:', step=1, value=5)  # default value 5, range 1-20
# news_count = st.sidebar.slider('Select the number of news items to display:', 1, 20, 5)  # default value 5, range 1-20

if st.sidebar.button("查看全部新聞"):
    news_count = len(news_data[category])
    st.sidebar.success(f"總共有 {news_count} 條新聞")

st.header(f'News in {category}')

count = 1
for news_title, news_url in news_data[category][:news_count]:  # Slicing the list based on slider value
    # Setting background color, border radius, and text alignment
    backgroundColor = "rgba(100, 100, 100, 0.65)"
    border_radius = "15px"
    text_style = "text-align: justify;"

    st.markdown(
        f'<div style="background-color: {backgroundColor}; padding: 10px; border-radius: {border_radius}; {text_style}">'
        f'<a href="{news_url}" style="text-decoration: none;" target="_blank"><h4>{count}. {news_title}</h4></a></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    count += 1

