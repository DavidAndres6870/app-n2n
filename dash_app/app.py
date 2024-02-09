# Import packages
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from decouple import config
import json

import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
#from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# Read API
    # define the scope and API credentials
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS = json.loads(config('CRED_GCP'))


    # add credentials to the account
credentials = ServiceAccountCredentials.from_json_keyfile_dict(CREDENTIALS, SCOPE)

    # authorize the clientsheet
client = gspread.authorize(credentials)

    # get the instance of the Spreadsheet
sheet = client.open('Copy of N2N - Database')

    # get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)

    # Incorporate data
data = sheet_instance.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])


# Figures

# Fig component 1

filtered_df = df[(df['Employment Status']!='') &
                 (df['Employment Status']!='Maternity Leave / Full-time Mom') &
                 (df['Employment Status']!='Entrepreneur')
                 ]
employment_status = filtered_df['Employment Status'].value_counts()
employment_status

fig1 = px.bar(x=employment_status.index, y=employment_status.values, labels={'x': 'Employment Status', 'y': 'Count'})

# Fig component 2
fig2 = px.pie(df, names='Format', title='Attendees by Event mode')

# Fig component 3
fig3 = px.pie(df, names='City', title='Attendees by City')

# Fig component 4
filtered_df = df[df['Country of Origin']!='']
top_6_countries = filtered_df['Country of Origin'].value_counts().nlargest(6)
top_6_countries_sorted = top_6_countries.sort_values(ascending=True)

fig4 = px.bar(x=top_6_countries_sorted.values, y=top_6_countries_sorted.index, labels={'x': '', 'y': 'Employment Status'}, title='Notworking2Networking attendance by Country')

# Fig component 5 (map)

# Count the number of occurrences of each country in the DataFrame
country_counts = df['Country of Origin'].value_counts().reset_index()
country_counts.columns = ['country', 'attendants']

fig5 = px.choropleth(
    country_counts,
    locations='country',
    locationmode='country names',
    color='attendants',
    hover_name='country',
    color_continuous_scale='Viridis_r',
    #range_color=[0,3000],
    title='NotWorking2Networking map',
)

fig5.update_geos(
    #showcountries =True,
    showcoastlines=True,
    coastlinecolor='RebeccaPurple',
    showland=True,
    landcolor='LightGrey',
    showocean=True,
    oceancolor='LightBlue',
    fitbounds= 'locations',
    projection_type='orthographic',
)

fig5.update_layout(
    geo=dict(showframe=False, showcoastlines=False),
    coloraxis_colorbar=dict(title='Attendants by country'),
)

# Fig component 6
df['Date'] = pd.to_datetime(df['Date'])

attendance_grouped = df.groupby(['Date', 'Attendance']).size().reset_index(name='count')
attendance_grouped.loc[attendance_grouped['Attendance'] == 'Attending', 'Attendance'] = 'Not Attending'
attendance_grouped['cumulative_count'] = attendance_grouped.groupby('Attendance')['count'].cumsum()
attendance_grouped['total_count'] = attendance_grouped['count'].cumsum()

fig6 = px.line(attendance_grouped, x='Date', y= 'total_count', markers=True, title='Attendance Count Over Time')
fig6.update_layout(yaxis_title='Attendants')

# Fig component61
toronto_season_attendance = df.loc[df['City']=='Toronto',['Season']]
toronto_season_attendance = toronto_season_attendance.groupby('Season').size().reset_index(name='Attendance')

fig61 = px.bar(toronto_season_attendance,x="Season", y="Attendance")
fig61.update_xaxes(tickmode='linear', dtick=1)

# Fig component62
montreal_season_attendance = df.loc[df['City']=='Montreal',['Season']]
montreal_season_attendance = montreal_season_attendance.groupby('Season').size().reset_index(name='Attendance')

fig62 = px.bar(montreal_season_attendance,x="Season", y="Attendance")
fig62.update_xaxes(tickmode='linear', dtick=1)

# Fig component 7
filtered_df = df[(df['Industry / Event']!='Workshop: LinkedIn Workshop to Advance Your Career') &
                 (df['Industry / Event']!='Workshop: Insider Secrets to Landing Ideal Jobs (for Newcomers)') &
                 (df['Industry / Event']!='Workshop: Secrets to Crafting The Perfect Job Application by Izzy Piyale-Sheard') &
                 (df['Industry / Event']!='Workshop: Top 22 Tips to Get a Job in 2022') &
                 (df['Industry / Event']!='Workshop: How to Write Business English (for Newcomers)') &
                 (df['Industry / Event']!='End of Season Online Meetup') &
                 (df['Industry / Event']!='S8 Party') &
                 (df['Industry / Event']!='End of Season In Person Meetup') &
                 (df['Industry / Event']!='S7 Party') &
                 (df['Industry / Event']!='Volunteer Training')]
#top_9_industry = filtered_df[['Industry / Event','Format']].value_counts().nlargest(9).to_frame().reset_index()
industry = filtered_df[['Industry / Event','Format']].value_counts().to_frame().reset_index()

fig7 = px.bar(industry,x='Industry / Event', y='count',color='Format', barmode='group',labels={'x': 'Industry / Event', 'y': 'Format'})
fig7.update_layout(yaxis_title='Total Attendance')

# Fig component 8
df_attendees = df[['#','Industry / Event', 'Format', 'Attendance']]
df_attendees = df_attendees[['#', 'Industry / Event','Format']].value_counts().sort_index().reset_index(name='Attendants')

df_average_attendees = df_attendees.groupby(['Industry / Event', 'Format']).agg({'Attendants': ['sum', 'count']}).reset_index()
df_average_attendees.columns = ['Industry / Event', 'Format', 'Sum_Count', 'Attendants']

df_average_attendees['Average']= df_average_attendees['Sum_Count']/df_average_attendees['Attendants']

filtered_df2 = df_average_attendees[(df_average_attendees['Industry / Event']!='Workshop: LinkedIn Workshop to Advance Your Career') &
                                    (df_average_attendees['Industry / Event']!='Workshop: Insider Secrets to Landing Ideal Jobs (for Newcomers)') &
                                    (df_average_attendees['Industry / Event']!='Workshop: Secrets to Crafting The Perfect Job Application by Izzy Piyale-Sheard') &
                                    (df_average_attendees['Industry / Event']!='Workshop: Top 22 Tips to Get a Job in 2022') &
                                    (df_average_attendees['Industry / Event']!='Workshop: How to Write Business English (for Newcomers)') &
                                    (df_average_attendees['Industry / Event']!='End of Season Online Meetup') &
                                    (df_average_attendees['Industry / Event']!='S8 Party') &
                                    (df_average_attendees['Industry / Event']!='End of Season In Person Meetup') &
                                    (df_average_attendees['Industry / Event']!='S7 Party') &
                                    (df_average_attendees['Industry / Event']!='Volunteer Training')]

#top_average = filtered_df2[['Industry / Event','Format']].value_counts().nlargest(9).to_frame().reset_index()
top_average = filtered_df2[['Industry / Event','Format','Average']].value_counts().to_frame().reset_index()

top_average =top_average.sort_values('Average',ascending=False)

fig8 = px.histogram(top_average,x='Industry / Event', y = 'Average',color='Format',  barmode='group')
fig8.update_layout(yaxis_title='Average')

#fig8 = px.histogram(top_average,x='Industry / Event',color='Format',  barmode='group')

# Initialize the app
#app = Dash(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR]) #LUX, FLATLY,

# Define the navbar
navbar = dbc.NavbarSimple(
    brand=html.Div([html.I(className="fas fa-chart-bar"), " Notworking2Networking"]),  # Bar chart icon
    brand_href="https://github.com/DavidAndres6870/n2n",
    color="darkblue",
    dark=True,
)


# App layout
app.layout = dbc.Container([
    # Navigation bar
    navbar,

    # Add space after the navigation bard
    html.Div(style={"height": "30px"}),

    html.Div(children='Notworking 2 Networking data'),
    #dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure = fig1),
    dcc.Graph(figure = fig2),
    dcc.Graph(figure = fig3),
    dcc.Graph(figure = fig4),
    dcc.Graph(figure = fig5),
    dcc.Graph(figure = fig6),
    dcc.Graph(figure = fig61),
    #dcc.Graph(figure = fig62),
    dcc.Graph(figure = fig7),
    dcc.Graph(figure = fig8),
    ])
'''app.layout = html.Div([
    html.Div(children='My First App with Data and a Graph'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    dcc.Graph(figure=px.histogram(df, x='continent', y='lifeExp', histfunc='avg'))
])'''


# Run the app
if __name__ == '__main__':
    app.run(debug=False)
    app.run_server(host="0.0.0.0", port="8050")

#port 8050