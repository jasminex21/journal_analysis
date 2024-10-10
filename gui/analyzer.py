import streamlit as st
import datetime
import io
import base64
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objects as go
import streamlit_wordcloud as wc
import matplotlib.pyplot as plt

def apply_theme(selected_theme):
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

    .stApp > header {{
        background-color: transparent;
    }}
    .stApp {{
        color: {selected_theme["text_color"]};
        font-family: 'Outfit', sans-serif;
    }}
    button[data-baseweb="tab"] {{
        background-color: transparent !important;
    }}
    div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > input, div[data-baseweb="base-input"] > textarea {{
        color: {selected_theme["text_color"]};
        -webkit-text-fill-color: {selected_theme["text_color"]} !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif;
    }}
    p, ul, li {{
        color: {selected_theme["text_color"]};
        font-weight: 600 !important;
        font-size: large !important;
        font-family: 'Outfit', sans-serif;
    }}
    h3, h2, h1, strong, h4 {{
        color: {selected_theme["text_color"]};
        font-weight: 900 !important;
        font-family: 'Outfit', sans-serif;
    }}
    [data-baseweb="tag"] {{
        color: {selected_theme["text_color"]};
        font-family: 'Outfit', sans-serif;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

THEME = {"background_color": "#212145",
         "button_color": "#1D1D34",
         "inputs": "#4e4466",
         "text_color": "white"}

st.title("Journal Analyzer")

apply_theme(THEME)

ENTRIES = pd.read_csv("/home/jasmine/PROJECTS/journal_analysis/data/OCT10.csv")
ENTRIES["date"] = pd.to_datetime(ENTRIES["date"])

stopwords = ["bc", "abt", "ve", "don", "didn", "ll", "got", 
             "haven", "go", "went", "re", "make", "wasn", 
             "really", "will", "wouldn", "put", "yet",
             "doesn", "took", "quite", "way", "actually", 
             "gonna", "still", "gotta"]

# TODO: need some way to programmatically determine max and min dates
# bc can't go into future or too far into past

# TODO: provide some stats abt the entries in the date range - how many
# entries total? avg word count?

# TODO: freq table - more manual than the WC package but for ease rn I'm 
# keeping the package implementation
today = datetime.datetime.now()
default_diff = datetime.timedelta(days=7)

with st.sidebar: 
    st.markdown("## Select Date Range to Analyze")
    st.date_input("Date range", 
                  value=(today - default_diff, today), 
                  min_value=datetime.date(2024, 1, 13),
                  max_value=today,
                  format="MM/DD/YYYY",
                  key="date_range")
    filtered_entries = ENTRIES[(ENTRIES["date"] >= pd.Timestamp(st.session_state.date_range[0])) & 
                               (ENTRIES["date"] <= pd.Timestamp(st.session_state.date_range[-1]))]
    
    all_text = " ".join(entry for entry in filtered_entries["entry"]).lower()
    # st.write(filtered_entries)

wordcloud = WordCloud(width=1000, height=700, background_color='white', 
                      min_word_length=2, stopwords=set(list(STOPWORDS)+stopwords), #-set(["he", "she", "him", "her"] )
                      max_words=300, margin=5, random_state=21,
                      relative_scaling="auto").generate(all_text) 

img = io.BytesIO()
plt.figure(figsize=(20, 12))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.savefig(img, format='png', bbox_inches='tight')
plt.close()

img.seek(0)
img_base64 = base64.b64encode(img.read()).decode('utf-8')

fig = go.Figure()

fig.add_layout_image(
    dict(
        source=f'data:image/png;base64,{img_base64}',
        xref="paper", yref="paper",
        x=0, y=1,  # Position: lower left
        sizex=1, sizey=1,
        xanchor="left", yanchor="top",
        layer="below"
    )
)

fig.update_layout(
    width=1000,
    height=700,
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
)
st.markdown(f"### WordCloud for {st.session_state.date_range[0].strftime('%m/%d/%Y')} to {st.session_state.date_range[-1].strftime('%m/%d/%Y')}")
st.plotly_chart(fig)

# return_obj = wc.visualize(filtered_entries, per_word_coloring=False)
# st.write(return_obj)
