import streamlit as st
import datetime
import io
import string
import base64
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import stopwords
import plotly.graph_objects as go
import streamlit_wordcloud as wordcloud
from nltk import ngrams
import matplotlib.pyplot as plt

st.set_page_config(layout='wide',
                   page_title="Journal Analyzer",
                   page_icon=":book:")

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

if "filtered_entries" not in st.session_state: 
    st.session_state.filtered_entries = None
if "all_words_and_bigrams" not in st.session_state: 
    st.session_state.all_words_and_bigrams = None
if "counts" not in st.session_state: 
    st.session_state.counts = None
if "word_dict" not in st.session_state: 
    st.session_state.word_dict = {}

st.title("Journal Analyzer")

apply_theme(THEME)

ENTRIES = pd.read_csv("/home/jasmine/PROJECTS/journal_analysis/data/2024-10-15_ENTRIES.csv")
ENTRIES["date"] = pd.to_datetime(ENTRIES["date"])

# removing punctuation
ENTRIES["entry"] = ENTRIES["entry"].str.replace(f'[{string.punctuation}]', '', regex=True)

STOPWORDS = stopwords.words("english")
addl_stopwords = ["i’m", "like", "abt", "bc", "really", "get", 
                 "i’ve", "i’d", "he’s", "got", "i’ll", "can’t",
                 "would", "could", "rlly", "he’d", "she’s", 
                 "she’d", "it’ll", "put", "let", "that’s", 
                 "there’s", "they’re"]
STOPWORDS += addl_stopwords
STOPWORDS = [word.replace("'", "’") for word in STOPWORDS]

def get_words_and_bigrams(text):

    words = [word.lower().strip() for word in text.split() if word.lower().strip() not in STOPWORDS]
    bigrams_list = list(ngrams(words, 2))
    return words + [' '.join(bigram) for bigram in bigrams_list]

# TODO: need some way to programmatically determine max and min dates
# bc can't go into future or too far into past

# TODO: provide some stats abt the entries in the date range - how many
# entries total? avg word count?

# TODO: freq table - more manual than the WC package but for ease rn I'm 
# keeping the package implementation
today = datetime.datetime.now()
last_date = ENTRIES["date"].iloc[-1].date()
default_diff = datetime.timedelta(days=7)

with st.sidebar: 
    st.markdown("## Select Date Range to Analyze")
    st.date_input("Date range", 
                  value=(today - default_diff, today), 
                  min_value=datetime.date(2024, 1, 13),
                  max_value=last_date,
                  format="MM/DD/YYYY",
                  key="date_range")
    
    st.session_state.filtered_entries = ENTRIES[(ENTRIES["date"] >= pd.Timestamp(st.session_state.date_range[0])) & 
                               (ENTRIES["date"] <= pd.Timestamp(st.session_state.date_range[-1]))]
    
    st.session_state.all_words_and_bigrams = st.session_state.filtered_entries["entry"].apply(get_words_and_bigrams).explode()

    st.session_state.counts = pd.DataFrame(st.session_state.all_words_and_bigrams.value_counts(), columns=['count']).reset_index()
    st.session_state.counts = st.session_state.counts.rename(columns={"entry": "text", "count": "value"})
    st.session_state.counts = st.session_state.counts[st.session_state.counts["text"].str.len() > 1]
    st.session_state.counts = st.session_state.counts.head(200)
    # st.session_state.word_dict = list(st.session_state.counts.T.to_dict().values())
    freqs = dict(zip(st.session_state.counts['text'].tolist(), st.session_state.counts['value'].tolist()))

wc = WordCloud(width=1000, height=600, max_words=200, 
               background_color='white',
               colormap="tab20b", random_state=21).generate_from_frequencies(freqs)
img = io.BytesIO()
plt.figure(figsize=(20, 12))
plt.imshow(wc, interpolation='bilinear')
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

cloud_col, table_col = st.columns([3, 1])

with cloud_col: 
    st.markdown(f"### WordCloud for {st.session_state.date_range[0].strftime('%m/%d/%Y')} to {st.session_state.date_range[-1].strftime('%m/%d/%Y')}")
    st.plotly_chart(fig)

with table_col: 
    st.markdown(f"### Frequency Table")
    st.dataframe(data=st.session_state.counts, use_container_width=True, height=600)