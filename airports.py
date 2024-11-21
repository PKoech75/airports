"""
Name: Phil Koechling
CS230: Section 5
Data: NE Airports
URL:

Description:
    This program serves the purpose of allowing the user to look at airport data by states within the new england reigon
    The main features of this program are the interactive map, that allows the user to see the airports in selected state,
    hovering over each dot will provide the airport name and elevation
    there is also a pie chart that shows ratio of airport types that are selected
    there is also a bar chart that shows the average elevation of airports in each selected state
    lastly a table that shows data about each selected airport

"""
import streamlit as st
import pandas as pd
import numpy as nmp
import matplotlib.pyplot as plt
import pydeck as pdk

allStates = ["US-MA", "US-ME", "US-CT", "US-NH", "US-VT", "US-RI"]
#Functions
#Func to read in data to program
def read_Airport_Data():
    return pd.read_csv("airports.csv").set_index("ident")


#Func to filter all airport data into NE airport data with, id, name, location, state. Also filters runway data
#[DA1]
def filter_Airport_Data(sel_States, sel_type, max_elevation):
    df = read_Airport_Data()
    df = df.loc[df['iso_region'].isin(sel_States)]
    df = df.loc[df['type'].isin(sel_type)]
    df = df.loc[df['elevation_ft']< max_elevation]
    return df


#[py2]
def count_Types(types, df):
    return [df.loc[df["type"].isin([type])].shape[0] for type in types]

#[py4]
def all_types():
    df = read_Airport_Data()
    lst = []

    for ind, row in df.iterrows():
        if row['type'] not in lst:
            lst.append(row['type'])

    return lst

#Func for creating dictionary of airports to elevations
#[py5][da4][da8]
def find_elevation(df):
    elevation = [row['elevation_ft'] for ind, row in df.iterrows()]
    states = [row['iso_region'] for ind, row in df.iterrows()]

    dict = {}

    for state in states:
        dict[state] = []

    for i in range(len(elevation)):
        dict[states[i]].append(elevation[i])
    return dict

#[da9]
def elevation_Avg(ele_dict):
    dict = {}

    for key in ele_dict.keys():
        dict[key] = nmp.mean(ele_dict[key])

    return dict

#Func to show a pie chart of number of airports by type
def generate_pie(counts, sel_type, sel_States):
    plt.figure()
    plt.pie(counts, labels=sel_type, autopct="%.2f")
    plt.title(f"Ratio of Airport types in: {", ".join(sel_States)}")
    return plt

#Func for table showing airport data for selected state
def airport_Table(df):
    if df.empty:
        st.write('no data to display')
    else:
        table_data = df[['name', 'elevation_ft']].rename(
            columns={
                'name': 'Airport Name',
                'elevation_ft': 'Elevation (ft)'
                })
        st.dataframe(table_data)

#Func for building a bar chart of avg airport elevation for each state
def airport_Chart(avg_dict):
    plt.figure()

    x = avg_dict.keys()
    y = avg_dict.values()
    plt.bar(x, y)
    plt.ylabel("Elevation in feet")
    plt.xlabel("States")
    plt.title(f"Average elevation of airports in:{' ,'.join(avg_dict.keys())}")

    return plt


#Func for state map
def airport_Map(df):
    map_df = df.filter(['name','latitude_deg','longitude_deg', 'elevation_ft'])

    view_state = pdk.ViewState(latitude=map_df["latitude_deg"].mean(),
                               longitude=map_df["longitude_deg"].mean(),
                               zoom = 5)

    layer = pdk.Layer("ScatterplotLayer",
                      data=map_df,
                      get_position= '[longitude_deg, latitude_deg]',
                      get_radius = 900,
                      get_color = [125,155,125],
                      pickable =True)



    tool_Tip = {'html': 'Airport Name:<br><b>{name}<br>Elevation:<br>{elevation_ft}<b/>', 'style': {'backgroundColor': 'steelblue', 'color': 'black'}}

    map = pdk.Deck(map_style='mapbox://styles/mapbox/dark-v11',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip = tool_Tip)

    st.pydeck_chart(map)





#Main func
def main():
   st.title('New England Airports')
   st.write('Explore the Airports of New England')

   #[st4]
   st.sidebar.write("select state or states to display data")
   #[st1]
   states = st.sidebar.multiselect('States: ', allStates)
   #[st2]
   max_elevation = st.sidebar.slider('Max Elevation: ', 0, 1500)
   #[st3]
   ap_types = st.sidebar.multiselect("Select an airport Type: ", all_types())

   data = filter_Airport_Data(states, ap_types, max_elevation)
   counts = count_Types(ap_types, data)

   if len(states) > 0 and max_elevation > 0 and len(ap_types) > 0:
       #[map]
       st.write('Map of Airports in selected states:')
       airport_Map(data)

       #[viz1]
       st.write("Pie Chart of airport types")
       pie_chart = generate_pie(counts, ap_types, states)
       st.pyplot(pie_chart)

       #[viz2]
       st.write("Bar chart of average elevation by state:")
       st.pyplot(airport_Chart(elevation_Avg(find_elevation(data))))

       #[viz3]
       st.write("Airport information:")
       airport_Table(data)

main()




