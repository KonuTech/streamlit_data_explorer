import streamlit as st
import numpy as np
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns


st.markdown("""
This app performs simple webscraping of NBA player stats data!
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/).
""")

st.sidebar.header("User Input Features")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(1950, 2023))))

@st.cache
def load_data(year):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df["Age"] == "Age"].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(["Rk", "3P%", "FG%", "2P%", "eFG%", "FT%"], axis=1)
    return playerstats

playerstats = load_data(selected_year)

sorted_unique_team = sorted(playerstats["Tm"].unique())
# selected_team = st.sidebar.multiselect("Team", sorted_unique_team, default="ATL")
selected_team = st.sidebar.multiselect("Team", options=sorted_unique_team, default=sorted_unique_team)

unique_pos = ["C", "PF", "SF", "PG", "SG"]
# selected_pos = st.sidebar.multiselect("Position", unique_pos, default="C")
selected_pos = st.sidebar.multiselect("Position", options=unique_pos, default=unique_pos)


df_selected_team = playerstats[(playerstats["Tm"].isin(selected_team)) & (playerstats["Pos"].isin(selected_pos))]

st.header("Display Player Stats of Selected Team(s)")
st.write("Data Dimension: " + str(df_selected_team.shape[0]) + " rows and " + str(df_selected_team.shape[1]) + " columns.")
st.dataframe(df_selected_team)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

if st.button("Correlation Heatmap"):
    st.header("Correlation Matrix Heatmap")
    df_selected_team.to_csv("output.csv", index=False)
    df = pd.read_csv("output.csv")

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        fig, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    st.pyplot(fig)
