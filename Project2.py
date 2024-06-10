import streamlit as st
from streamlit_option_menu import option_menu
import psycopg2
import pandas as pd
import plotly.express as px
import requests
import json

# Database connection
mydb = psycopg2.connect(
    host="localhost",
    user="postgres",
    port="5432",
    database="phonepe_data",
    password="Vivek@1991"
)
cursor = mydb.cursor()

# Function to fetch data from the database
def fetch_data(query, columns):
    cursor.execute(query)
    mydb.commit()
    table = cursor.fetchall()
    return pd.DataFrame(table, columns=columns)

# DataFrames creation
Aggre_insurance = fetch_data("SELECT * FROM aggregated_insurance", ["States", "Years", "Quarter", "Transaction_type", "Transaction_count", "Transaction_amount"])
Aggre_transaction = fetch_data("SELECT * FROM aggregated_transaction", ["States", "Years", "Quarter", "Transaction_type", "Transaction_count", "Transaction_amount"])
Aggre_user = fetch_data("SELECT * FROM aggregated_user", ["States", "Years", "Quarter", "Brands", "Transaction_count", "Percentage"])
map_insurance = fetch_data("SELECT * FROM map_insurance", ["States", "Years", "Quarter", "District", "Transaction_count", "Transaction_amount"])
map_transaction = fetch_data("SELECT * FROM map_transaction", ["States", "Years", "Quarter", "District", "Transaction_count", "Transaction_amount"])
map_user = fetch_data("SELECT * FROM map_user", ["States", "Years", "Quarter", "District", "RegisteredUsers", "AppOpens"])
top_insurance = fetch_data("SELECT * FROM top_insurance", ["States", "Years", "Quarter", "Pincodes", "Transaction_count", "Transaction_amount"])
top_transaction = fetch_data("SELECT * FROM top_transaction", ["States", "Years", "Quarter", "Pincodes", "Transaction_count", "Transaction_amount"])
top_user = fetch_data("SELECT * FROM top_user", ["States", "Years", "Quarter", "Pincodes", "RegisteredUsers"])

# Fetch geojson data
url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
response = requests.get(url)
data1 = json.loads(response.content)

# Function to display transaction amount and count by year
def Transaction_amount_count_Y(df, Year):
    tacy = df[df["Years"] == Year]
    tacy.reset_index(drop=True, inplace=True)
    tacyg = tacy.groupby("States")[["Transaction_count", "Transaction_amount"]].sum()
    tacyg.reset_index(inplace=True)
    return tacyg

# Function to display user data by year
def Aggre_user_plot_1(df, Year):
    user_year = df[df["Years"] == Year]
    user_year.reset_index(drop=True, inplace=True)
    user_agg = user_year.groupby("States")[["Transaction_count", "Percentage"]].sum()
    user_agg.reset_index(inplace=True)
    return user_agg

# Map insurance district
def Map_insur_District(df, state):
    tacy = df[df["States"] == state]
    tacy.reset_index(drop=True, inplace=True)

    # Group by "Transaction_type" and sum "Transaction_count" and "Transaction_amount"
    tacyg = tacy.groupby("District")[["Transaction_count", "Transaction_amount"]].sum()
    tacyg.reset_index(inplace=True)

    # Create a bar chart for transaction amount
    fig_bar_1 = px.bar(tacyg, x="Transaction_amount", y="District", orientation="h",
                       title=f"{state.upper()} DISTRICT AND TRANSACTION AMOUNT", color_discrete_sequence=px.colors.sequential.Mint_r)
    st.plotly_chart(fig_bar_1)

    # Create a bar chart for transaction count
    fig_bar_2 = px.bar(tacyg, x="Transaction_count", y="District", orientation="h",
                       title=f"{state.upper()} DISTRICT AND TRANSACTION COUNT", color_discrete_sequence=px.colors.sequential.Mint_r)
    st.plotly_chart(fig_bar_2)

def map_user_plot_1(df, year):
 muy = df[df["Years"] == year]
 muy.reset_index(drop=True, inplace=True)
    
 muyg = muy.groupby("States")[["RegisteredUsers", "AppOpens"]].sum()
 muyg.reset_index(inplace=True)

 fig_line_1 = px.line(muyg, x="States", y=["RegisteredUsers", "AppOpens"],
                         title= f"{year} REGISTERED USERS AND APP OPENS IN 2024", width=1000, height=800, markers=True)
 fig_line_1.show()
 
 return muy

# Streamlit App Configuration
st.set_page_config(layout="wide")
st.title("Phonepe Pulse Data Visualization and Exploration")

# Sidebar menu
with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Data Exploration", "Top Charts"])

if select == "Home":
    
    col1,col2= st.columns(2)

    with col1:
        st.header("PHONEPE")
        st.subheader("INDIA'S BEST TRANSACTION APP")
        st.markdown("PhonePe is an Indian digital payments and financial technology company")
        st.write("*****FEATURES****")
        st.write("****Credit & Debit card linking****")
        st.write("****Bank Balance Check****")
        st.write("****Money Storage****")
        st.write("****PIN Authorization****")
        st.download_button("DOWNLOAD THE APP NOW", "https://www.phonepe.com/app-download/")

    with col2:
        st.image("C:\Users\Vivek\Desktop\download.jpg")
    
elif select == "Data Exploration":
    tab1, tab2, tab3 = st.tabs(["Aggregated Analysis", "Map Analysis", "Top Analysis"])

    with tab1:
        method = st.radio("Select the method", ["Insurance Analysis", "Transaction Analysis", "User Analysis"])
        
        if method == "Insurance Analysis":
            years = st.slider("Select The Year", min_value=int(Aggre_insurance["Years"].min()))
            tacyg = Transaction_amount_count_Y(Aggre_insurance, years)
            
            col1, col2 = st.columns(2)
            with col1:
                fig_amount = px.bar(tacyg, x="States", y="Transaction_amount", title="TRANSACTION AMOUNT",
                                    color_discrete_sequence=px.colors.sequential.Aggrnyl, height=650, width=600)
                st.plotly_chart(fig_amount)
            with col2:
                fig_count = px.bar(tacyg, x="States", y="Transaction_count", title="TRANSACTION COUNT",
                                   color_discrete_sequence=px.colors.sequential.Blackbody_r, height=650, width=600)
                st.plotly_chart(fig_count)

            fig_india_1 = px.choropleth(tacyg, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                                        color="Transaction_amount", color_continuous_scale="Rainbow",
                                        range_color=(tacyg["Transaction_amount"].min(), tacyg["Transaction_amount"].max()),
                                        hover_name="States", title="TRANSACTION AMOUNT", fitbounds="locations",
                                        height=600, width=600)
            st.plotly_chart(fig_india_1)

            fig_india_2 = px.choropleth(tacyg, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                                        color="Transaction_count", color_continuous_scale="Rainbow",
                                        range_color=(tacyg["Transaction_count"].min(), tacyg["Transaction_count"].max()),
                                        hover_name="States", title="TRANSACTION COUNT", fitbounds="locations",
                                        height=600, width=600)
            st.plotly_chart(fig_india_2)

        elif method == "Transaction Analysis":
            years = st.slider("Select The Year", min_value=int(Aggre_transaction["Years"].min()))
            tacyg = Transaction_amount_count_Y(Aggre_transaction, years)
            
        col1, col2 = st.columns(2)
        with col1:
                fig_amount = px.bar(tacyg, x="States", y="Transaction_amount", title="TRANSACTION AMOUNT",
                                    color_discrete_sequence=px.colors.sequential.Aggrnyl, height=650, width=600)
                st.plotly_chart(fig_amount)
        with col2:
                fig_count = px.bar(tacyg, x="States", y="Transaction_count", title="TRANSACTION COUNT",
                                   color_discrete_sequence=px.colors.sequential.Blackbody_r, height=650, width=600)
                st.plotly_chart(fig_count)

        fig_india_1 = px.choropleth(tacyg, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                                        color="Transaction_amount", color_continuous_scale="Rainbow",
                                        range_color=(tacyg["Transaction_amount"].min(), tacyg["Transaction_amount"].max()),
                                        hover_name="States", title="TRANSACTION AMOUNT", fitbounds="locations",
                                        height=600, width=600)
        st.plotly_chart(fig_india_1)

        fig_india_2 = px.choropleth(tacyg, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                                        color="Transaction_count", color_continuous_scale="Rainbow",
                                        range_color=(tacyg["Transaction_count"].min(), tacyg["Transaction_count"].max()),
                                        hover_name="States", title="TRANSACTION COUNT", fitbounds="locations",
                                        height=600, width=600)
        st.plotly_chart(fig_india_2)

        col1, col2 = st.columns(2)
        with col1:
                states = st.selectbox("Select the state", Aggre_transaction["States"].unique())
                tacy_state = Aggre_transaction
        
import streamlit as st
import plotly.express as px
import pandas as pd
import json

# Placeholder function definitions (replace with actual implementations)
def Transaction_amount_count_Y(Aggre_transaction, year):
    # Implement this function to filter and return the relevant data for the selected year
    return Aggre_transaction[Aggre_transaction["Years"] == year]

# Load your data here
Aggre_transaction = pd.read_csv("your_transaction_data.csv")

# Load your geojson data
with open("path_to_your_geojson_file.geojson") as response:
    data1 = json.load(response)

# Main code for "Transaction Analysis" and "Map Transaction"
st.title("Transaction Analysis")

method = st.selectbox("Select Method", ["Transaction Analysis", "Map Transaction"])

if method == "Transaction Analysis":
    years = st.slider("Select The Year", min_value=int(Aggre_transaction["Years"].min()), 
                      max_value=int(Aggre_transaction["Years"].max()), value=int(Aggre_transaction["Years"].min()))
    tacyg = Transaction_amount_count_Y(Aggre_transaction, years)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_amount = px.bar(tacyg, x="States", y="Transaction_amount", title="TRANSACTION AMOUNT",
                            color_discrete_sequence=px.colors.sequential.Aggrnyl, height=650, width=600)
        st.plotly_chart(fig_amount)
    
    with col2:
        fig_count = px.bar(tacyg, x="States", y="Transaction_count", title="TRANSACTION COUNT",
                           color_discrete_sequence=px.colors.sequential.Blackbody_r, height=650, width=600)
        st.plotly_chart(fig_count)

    fig_india_1 = px.choropleth(tacyg, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                                color="Transaction_amount", color_continuous_scale="Rainbow",
                                range_color=(tacyg["Transaction_amount"].min(), tacyg["Transaction_amount"].max()),
                                hover_name="States", title="TRANSACTION AMOUNT", fitbounds="locations",
                                height=600, width=600)
    st.plotly_chart(fig_india_1)

    fig_india_2 = px.choropleth(tacyg, geojson=data1, locations="States", featureidkey="properties.ST_NM",
                                color="Transaction_count", color_continuous_scale="Rainbow",
                                range_color=(tacyg["Transaction_count"].min(), tacyg["Transaction_count"].max()),
                                hover_name="States", title="TRANSACTION COUNT", fitbounds="locations",
                                height=600, width=600)
    st.plotly_chart(fig_india_2)

    col1, col2 = st.columns(2)
    
    with col1:
        states = st.selectbox("Select the state", Aggre_transaction["States"].unique())
        tacy_state = Aggre_transaction[Aggre_transaction["States"] == states]
        st.write(tacy_state)

elif method == "Map Transaction":
    years = st.slider("Select The Year", min_value=int(Aggre_transaction["Years"].min()), 
                      max_value=int(Aggre_transaction["Years"].max()), value=int(Aggre_transaction["Years"].min()))
    tacyg = Transaction_amount_count_Y(Aggre_transaction, years)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_amount = px.bar(tacyg, x="States", y="Transaction_amount", title="TRANSACTION AMOUNT",
                            color_discrete_sequence=px.colors.sequential.Aggrnyl, height=650, width=600)
        st.plotly_chart(fig_amount)
    
    with col2:
        fig_count = px.bar(tacyg, x="States", y="Transaction_count", title="TRANSACTION COUNT",
                           color_discrete_sequence=px.colors.sequential.Blackbody_r, height=650, width=600)
        st.plotly_chart(fig_count)
