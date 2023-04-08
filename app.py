############################################
# This code was tested using Google Chrome #
############################################

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
import dash_daq as daq

css_directory = os.getcwd()

# --------------------------------------------
# Load data
df = pd.read_excel('locations.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
df['Price'] = df['Price'].str.replace(',', '')
df['Price'] = df['Price'].astype(float)
df['Location'] = df['Location'].astype(str)
df1 = df.copy()

filtered_data = pd.read_excel('race_plot_top_10.xlsx', index_col=0)
pie_chart = pd.read_excel('pie_chart.xlsx')
pie_chart2 = pd.read_excel('pie_chart2.xlsx')
line_chart2 = pd.read_excel('line_chart2.xlsx')
mapamundo = pd.read_excel('mapamundo.xlsx')

# List of available companies
available_companies = list(df['Company'].unique())

# Filter for pie chart
company_name = 'NASA'
df_empresa = df[df['Company'] == company_name]

# Pie chart colors
color_map_success_failure = {'Success': 'green', 'Failure': '#E70000', 'Partial Failure':'#E8DD01', 'Prelaunch Failure':'#E88301'}
color_map_active_retired = {'Active': 'green', 'Retired': '#E70000'}

# Mission Status pie chart
pie1 = px.pie(pie_chart, names='Mission Status', values='count',
            title='Percentual de Sucesso e Falha GERAL para a Empresa ' + company_name,
            color='Mission Status', hover_data=['count'],
            color_discrete_map=color_map_success_failure)\
    .update_layout(plot_bgcolor = "rgba(0,0,0,0)", paper_bgcolor = "rgba(0,0,0,0)")

# Rocket Status pie chart
pie2 = px.pie(pie_chart2, names='Rocket Status', values='count',
            title='Percentual de Retired e Active GERAL para a Empresa ' + company_name,
            color='Rocket Status', hover_data=['count'],
            color_discrete_map=color_map_success_failure)\
    .update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

# Raceplot
raceplot = px.histogram(filtered_data , x="cumsum", y="Company", color="Company",
                 animation_frame="year",
                 range_x=[0,filtered_data['cumsum'].max()+5],
            )\
    .update_yaxes(showticklabels=True, showgrid=True, gridwidth=8)\
    .update_traces(hovertemplate=None).update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=25, color='#a5a7ab'),
        font=dict(color='#000000'),
        #legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        showlegend=False
    )

# Linechart

frames = []
years = []
counts = []
max_count = line_chart2["count"].max() + 5

for idx, _df in line_chart2.iterrows():
    years.append(_df["year"])
    counts.append(_df["count"])

    labels = [""] * (len(years) - 1)
    labels.append(_df["count"])

    sizes = [1] * (len(years) - 1)
    sizes.append(10)

    frames.append(
        go.Frame(
            data=[go.Scatter(
                x=years,
                y=counts,
                mode='lines+markers+text',
                text=labels,
                marker=dict(size=sizes),
                hovertext=labels,
                textposition="top center",
                textfont=dict(size=16),
                hovertemplate=None,
                line=dict(color="#37425B", width=2))
            ]
        )
    )

line_chart = go.Figure(
    data=[go.Scatter(x=[-10, -10], y=[-10, -10])],
    layout=go.Layout(
        xaxis=dict(range=[1957, 2022], autorange=False),
        yaxis=dict(range=[0, max_count], autorange=False),
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(
                        label='Play',
                        method='animate',
                        args=[None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                    ),
                    dict(
                        label='Pause',
                        method='animate',
                        args=[[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                                       'transition': {'duration': 0}}]
                    )
                ],
                # Position of buttons in the plot, side by side
                # Button width
                xanchor='right',
                yanchor='top',
                pad=dict(t=0, r=20),
            )
        ],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    ),
    frames=frames
)

# Mapbox scatter
mapamundo1 = px.scatter_mapbox(
    mapamundo, lat=mapamundo['Latitude'], lon=mapamundo['Longitude'],color="Company",
    zoom=2, size=[x*4 for x in list(mapamundo['count'].values)], height = 500,
    # Center of map
    center={"lat": 0, "lon": 0},
)

mapamundo1.update_layout(
    mapbox_style="open-street-map",
    plot_bgcolor="rgba(0,0,0,0)", 
    paper_bgcolor="rgba(0,0,0,0)",
    mapbox=dict(
        zoom=10,
    ),
    margin=dict(l=10, r=10, t=40, b=100),
)

# --------------------------------------------
# Define the app
# Load the styles.css
app = dash.Dash(__name__, external_stylesheets=['static/styles.css'])

server = app.server

# Define column 1, row 1
row_1_column_1 = html.Div(
    [
        html.H2("1. Evolution of the Number of Launches per year", style={'font-size':'18px', 'float': 'left', 'margin-left':'10px'}),
        html.P("Find Launch Hotspots: Discover top space race companies on our global map.", style={'font-size':'12px', 'float': 'left', 'margin-left':'12px', 'margin-top':'-10px', 'text-align':'left'}),
        html.Br(),
        html.Br(),
        dcc.Graph(
            id='mapa_slider',
            style={'background-color':'transparent'},
            config= {'displaylogo': False}
        ),
        html.Br(),
        html.Div(
            [html.Div(id='slider_container', 
                      children=[daq.Slider(id='slider_id', 
                                           handleLabel={"showCurrentValue": True,"label": "Year"}, color = '#37425B', min=1957, max=2022, value=1957,
                                           marks={'1957': '1957', '1962': '1962', '1967': '1967',
                                                    '1972': '1972', '1977': '1977', '1982': '1982',
                                                    '1987': '1987', '1992': '1992', '1997': '1997',
                                                    '2002': '2002', '2007': '2007', '2012': '2012',
                                                    '2017': '2017', '2022': '2022'}, size=475)],
                      style={
                          'margin-left': '5%',
                          'margin-top': '-90px',
                          'width': '100%'
                      }
                      )
             ],
            style={
                'width': '55%',
                'float': 'left',
                'height': '80px',
                'display': 'flex',
                'flex-direction': 'column'
            }
        )
    ],
    className="plot_container",
    style={'width': '55%', 'float': 'left', 'height': '520px'}
)

# Dropdown choose a company
choose_a_company = html.Div(
    [
        html.P("Choose a company:", style={'text-align': 'left', 'margin-left':'20px'}),
        dcc.Dropdown(
            id='company-dropdown',
            options=[{'label': company, 'value': company} for company in available_companies],
            value='NASA', placeholder='Filter by location ...',
            clearable=False, style={'width': '96.5%', 'margin-left':'10px', 'margin-top':'-5px'}),
    ],
    className="plot_container",
    style={'width': '100%', 'display': 'inline-block', 'height': '90px', 'margin-bottom':'5px' }
)

# Pie charts
pie_chart = html.Div(
    [
        html.H2("2. Success Rate of the Launch & Rocket Status", style={'font-size':'17.5px', 'float': 'left', 'margin-left':'5px'}),
        html.Div([
            html.Div([dcc.Graph(id='mission-status-pie-chart', config= {'displaylogo': False})],
                    style={'width': '50%', 'float': 'left', 'margin-top':'-60px'},
                    ),
            html.Div([dcc.Graph(id='rocket-status-pie-chart', config= {'displaylogo': False})],
                    style={'width': '50%', 'float': 'left', 'margin-top':'-60px'},
                    )
        ])
    ],
    className="plot_container",
    style={'width': '100%', 'height': '405px', 'display': 'inline-block','font-size':'11px','margin-bottom':'-30px'}
)

# Define column 2, row 1
row_1_column_2 = html.Div(
    [
        choose_a_company,
        pie_chart
    ],
    className="row",
    style={'width': '38%', 'height': '630px', 'display': 'inline-block', 'margin-bottom':'-30px'}
)

# Define column 1, row 2
row_2_column_1 = html.Div(
    [
        html.H2("3. The Race to the Stars", style={'font-size':'18px', 'float': 'left', 'margin-left':'10px'}),
        html.Br(),
        html.Br(),
        html.P("Top 10 Launch Leaders: See which companies are leading the race in space exploration.",
               style={'font-size':'12px', 'float': 'left', 'margin-left':'12px', 'margin-top':'-10px', 'text-align':'left'}),
        html.Br(),
        html.Br(),
        dcc.Graph(
            id='mapa_slider2',
            style={'background-color':'transparent','margin-top':'-25px'},
            config= {'displaylogo': False}
        ),
        html.Br(),

        html.Div(
            [html.Div(
                id='slider_container2', 
                children=[
                    daq.Slider(id='slider_id2', handleLabel={"showCurrentValue": True,"label": "Year"}, color = '#37425B', min=1957, max=2022, value=1957,
                        marks={'1957': '1957', '1962': '1962', '1967': '1967',
                                '1972': '1972', '1977': '1977', '1982': '1982',
                                '1987': '1987', '1992': '1992', '1997': '1997',
                                '2002': '2002', '2007': '2007', '2012': '2012',
                                '2017': '2017', '2022': '2022'}, size=450)],
                      style={
                          'padding': '5px', # espaço ao redor do slider
                          'margin-left': '39%',
                          'margin-top': '-35px',
                          'width': '90%'
                      }
                      )
             ],
            style={
                'width': '55%',
                'float': 'left',
                'height': '80px',
                'display': 'flex',
                'flex-direction': 'column'
            }
        )
    ],
    className="plot_container",
    style={'width': '55%', 'float': 'left', 'height': '550px', 'display': 'inline-block', 'margin-top':'-30px', 'margin-bottom':'10px'}
)

# Define column 2, row 2
row_2_column_2 = html.Div([
    html.H2("4. Growth of Rocket Launches per year", style={'font-size': '18px', 'float': 'left', 'margin-left': '10px'}),
    dcc.Graph(
        figure=line_chart,
        style={'width': '100%', 'float': 'left', 'margin-top': '-60px'},
        config= {'displaylogo': False}
    ),
    html.Div([
        html.P("Explore the trends in rocket launches over time with our interactive line chart. Hover over each point to discover the number of launches per year and dive deeper into the data by adjusting the date range.", style={'color': '#000000', 'margin-top': '-1px'})
    ], className='box_comment', style={'width': '90%', 'height': '55px', 'margin-bottom': '20px', 'margin-left':'15px', 'display': 'flex', 'flex-direction': 'column'}),
], className="plot_container", style={'width': '38%', 'float': 'left', 'height': '550px', 'display': 'inline-block', 'margin-top':'-30px', 'margin-bottom':'10px'})

# Group info and sources
Grupo = html.Div([
    html.Div([
        html.P(['Group Information:', html.Br(), 'Luis Gonçalves (20220624), Margarida Ferreira (20220677)',html.Br(), 'Mariana Água (20220704), Nádia Carvalho (20220700)'], style={'font-size': '12px', 'color':'white','text-align': 'left', 'margin-left':'10px'})
    ], style={'width': '55%', 'margin-top':'-6px'}),
    html.Div([
        html.P(['Sources: ',
                html.Br(),
                html.A('MAVEN ANALYTICS',
                       href='https://www.mavenanalytics.io/data-playground?accessType=open&search=MISSION',
                       target='_blank')], style={'font-size': '12px', 'color':'white', 'text-align': 'left', 'margin-top':'5px'})
    ],style={'width': '37%', 'margin-top':'7px', 'margin-left':'68px'})
], className='footerr', style={'display': 'flex', 'height': '60px', 'width':'98%', 'margin-top':'1px'})

# Row 1
row_1 = html.Div(
    [
    row_1_column_1, row_1_column_2
    ],
    className="row"
)

# Row 2
row_2 = html.Div(
    [
    row_2_column_1, row_2_column_2
    ],
    className="row"
)

# Define the body
body = html.Div([row_1, row_2],
className="row", style={'width': '100%', 'float': 'left', 'display': 'inline-block'})

# Define the footer
footer = html.Div(
    [
        Grupo
    ],
    className="footer", style={'margin-top': '10px', 'width': '100%', 'float': 'left', 'display': 'inline-block'}
)

# Define the app layout
app.title = 'Space Journey'
app.layout = html.Div([
    # Side bar
    html.Div([
        html.Br(),
        html.H1(children='SPACE JOURNEY'),
        html.Div([
            html.Br(),
            html.P("Explore the Universe with us!", style={'text-align': 'justify', 'color': '#ffffff'}),
            html.P("With this space mission dashboard, travel through time with this interactive platform that presents more detailed mission data.", style={'text-align': 'justify', 'color': '#ffffff'}),
            html.P("Join us on this space adventure and discover the incredible world beyond our planet!", style={'text-align': 'justify', 'color': '#ffffff'}),
], style={'color': '#ffffff'}),
        html.Img(src='static/fog_3.png', style={'width': '100%', 'position':'relative'})
    ], className='side_bar'),
    html.Div(
        children=[body, footer],
        className="mainpage_container",
        style={'width': '81%', 'float': 'right', 'display': 'inline-block', 'height': '1205px'}
    )
],
    className="mainpage"
)

@app.callback(
    dash.dependencies.Output('mapa_slider', 'figure'),
    [dash.dependencies.Input('slider_id', 'value')])
def update_mapa_slider(year):
    # Filter the dataframe for the selected year
    df = mapamundo[mapamundo['year'] == year]

    # Create a new map figure with the filtered data
    fig = px.scatter_mapbox(
        df, lat=df['Latitude'], lon=df['Longitude'], color="Company",
        zoom=0.1, size=[x * 4 for x in list(df['count'].values)], height=500,
        center={"lat": 43, "lon": 30},
    )
    fig.update_layout(
        autosize=False, 
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        mapbox_style="open-street-map",
        margin=dict(l=10, r=10, t=40, b=100),
        mapbox=dict(
            zoom=0.1, # set a fixed zoom level 0.75
        )
    )

    return fig

@app.callback(
    dash.dependencies.Output('mapa_slider2', 'figure'),
    [dash.dependencies.Input('slider_id2', 'value')])
def update_mapa_slider(year):
    # filter the dataframe for the selected year
    filtered_data1 = filtered_data[filtered_data['year'] == year]

    # create a new map figure with the filtered data
    fig = px.histogram(filtered_data1, x="cumsum", y="Company", color="Company",
                            animation_frame="year",
                            range_x=[0, filtered_data['cumsum'].max() + 5],
                            ) \
        .update_yaxes(showticklabels=True, showgrid=True, gridwidth=8) \
        .update_traces(hovertemplate=None).update_layout(xaxis_title="Total launches",
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        title_font=dict(size=25, color='#a5a7ab'),
        font=dict(color='#000000'),
        # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        showlegend=False
    )

    return fig

# Define a callback to update the mission status graph
@app.callback(
    dash.dependencies.Output('mission-status-pie-chart', 'figure'),
    [dash.dependencies.Input('company-dropdown', 'value')])
def update_mission_status_pie_chart(company_name):
    # Filter the dataframe for the selected company
    df_empresa = df[df['Company'] == company_name]

    # Count the mission status
    df_empresa = df_empresa['Mission Status'].value_counts().to_frame().reset_index()

    # Rename columns
    df_empresa.columns = ['Mission Status', 'count']

    # Create the pie chart
    fig = px.pie(df_empresa, names='Mission Status', values='count',
                 #title='Success & failure rate ',# + company_name,
                 color='Mission Status', hover_data=['count'],
                 color_discrete_map=color_map_success_failure,
                 width=250, height=400,
    ) 

    # White colored text and no background
    fig.update_layout(autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',

        #legend position at the bottom, center
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="center",
            x=0.5,
            
        ),
        margin=dict(l=10, r=30, t=50, b=20),
    )

    return fig

# Define a callback to update the rocket status graph
@app.callback(
    dash.dependencies.Output('rocket-status-pie-chart', 'figure'),
    [dash.dependencies.Input('company-dropdown', 'value')])

def update_rocket_status_pie_chart(company_name):
    # Filter the dataframe for the selected company
    df_empresa = df[df['Company'] == company_name]

    # Count the rocket status
    df_empresa = df_empresa['Rocket Status'].value_counts().to_frame().reset_index()

    # Rename columns
    df_empresa.columns = ['Rocket Status', 'count']

    # Create the pie chart
    fig = px.pie(df_empresa, names='Rocket Status', values='count',
                 #title='Active and retired rockets ',#  + company_name,
                 color='Rocket Status', hover_data=['count'],
                 color_discrete_map=color_map_active_retired,
                 width=250, height=400)

    fig.update_layout(autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #legend position at the bottom, center
        legend=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=10, r=30, t=50, b=20),
    )

    return fig

# --------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
