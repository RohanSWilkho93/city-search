# -*- coding: utf-8 -*-
import dash
import math
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

external_stylesheets = ['Design_2.css']

df = pd.read_csv("data.csv")
dff = pd.read_csv("standardized.csv") # contains normalized values


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

politics = ['Democrat', 'Republican', 'Independent']

colors = {
    'background': '#66B2FF',
    'text': '#00000'
}

def rank_cities(politics, rent, cost, internet, popden, air, traffic, safety_lev, walking, pizza_rating, graduates, singles, religion, rank_num):
    global dff
    # normalize first
    walking = (walking - df['gradeWalking'].min())/(df['gradeWalking'].max() - df['gradeWalking'].min()); internet = (internet - df['avgInternetSpeed'].min())/(df['avgInternetSpeed'].max() - df['avgInternetSpeed'].min())
    popden = (popden - df['avgPopulationDensity'].min())/(df['avgPopulationDensity'].max() - df['avgPopulationDensity'].min()); graduates = (graduates - df['percentGraduates'].min())/(df['percentGraduates'].max() - df['percentGraduates'].min());
    non_religion = ((1-religion) - df['percentNonReligious'].min())/(df['percentNonReligious'].max() - df['percentNonReligious'].min()); religion = (religion - df['percentReligious'].min())/(df['percentReligious'].max() - df['percentReligious'].min())
    singles = (singles - df['percentSingle'].min())/(df['percentSingle'].max() - df['percentSingle'].min()); rent = (rent - df['avgHomePrice'].min())/(df['avgHomePrice'].max() - df['avgHomePrice'].min());
    cost = (cost - df['avgCostOfLiving'].min())/(df['avgCostOfLiving'].max() - df['avgCostOfLiving'].min())
    air = (air - df['gradeAirQuality'].min())/(df['gradeAirQuality'].max() - df['gradeAirQuality'].min()); traffic = (traffic - df['gradeLowTraffic'].min())/(df['gradeLowTraffic'].max() - df['gradeAirQuality'].min())
    safety_lev = (safety_lev - df['gradeSafety'].min())/(df['gradeSafety'].max() - df['gradeSafety'].min()); pizza_rating = (pizza_rating - df['pizzaRatingAvg'].min())/(df['pizzaRatingAvg'].max() - df['pizzaRatingAvg'].min())
    if(politics == 'Democrat'):
        democrat = (1 - df['percentDemocrat'].min())/(df['percentDemocrat'].max() - df['percentDemocrat'].min())
        independent = (0 - df['percentIndependent'].min())/(df['percentIndependent'].max() - df['percentIndependent'].min())
        republican = (0 - df['percentRepublican'].min())/(df['percentRepublican'].max() - df['percentRepublican'].min())
    elif(politics == 'Republican'):
        democrat = (0 - df['percentDemocrat'].min())/(df['percentDemocrat'].max() - df['percentDemocrat'].min())
        independent = (1 - df['percentIndependent'].min())/(df['percentIndependent'].max() - df['percentIndependent'].min())
        republican = (0 - df['percentRepublican'].min())/(df['percentRepublican'].max() - df['percentRepublican'].min())
    else:
        democrat = (0 - df['percentDemocrat'].min())/(df['percentDemocrat'].max() - df['percentDemocrat'].min())
        independent = (0 - df['percentIndependent'].min())/(df['percentIndependent'].max() - df['percentIndependent'].min())
        republican = (1 - df['percentRepublican'].min())/(df['percentRepublican'].max() - df['percentRepublican'].min())

    # classifying the Group

    test_1 = [popden,rent,democrat]
    array_1 = dff[['avgPopulationDensity','avgHomePrice', 'percentDemocrat']].to_numpy()
    array_2 = dff['group'].to_numpy()

    distance_1 = dict()
    for i in range(array_1.shape[0]): distance_1.update({i:(np.linalg.norm(array_1[i] - test_1))})
    distance_1 = {k: v for k, v in sorted(distance_1.items(), key=lambda item: item[1])}

    distance_1_top_keys = list(distance_1.keys())[:5] # 5 nearest neighbours

    group_list = list()
    for key in distance_1_top_keys:
        group_list.append(array_2[key])

    grp = max(set(group_list), key = group_list.count)

    # ranking cities closest in the classified group
    test = [walking, internet, graduates, independent, non_religion, religion, republican, singles, cost, air, traffic, safety_lev, pizza_rating]

    dff = dff.loc[dff['group'] == grp]
    array = dff[['gradeWalking','avgInternetSpeed','percentGraduates','percentIndependent','percentNonReligious','percentReligious','percentRepublican','percentSingle','avgCostOfLiving','gradeAirQuality','gradeLowTraffic','gradeSafety','pizzaRatingAvg']].to_numpy()
    distance = dict()

    for i in range(array.shape[0]):
        distance.update({i:(np.linalg.norm(array[i] - test))})

    max_distance = max(distance.values())
    min_distance = min(distance.values())
    scores = dict(); rank = dict()

    cities = dff['city'].to_numpy()
    ids = dff['id'].to_numpy()

    rank_num = math.ceil(rank_num)
    rank_num = min([dff.shape[0], rank_num])

    distance = {k: v for k, v in sorted(distance.items(), key=lambda item: item[1])}
    distance_top_keys = list(distance.keys())[:rank_num]

    top_cities = list()
    top_ids = list()

    rank_counter = 1
    for key in distance_top_keys:
        scores.update({key:(max_distance - distance[key])/(max_distance - min_distance)})
        scores[key] = round(scores[key],4)
        rank.update({key:rank_counter}); rank_counter += 1

    scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[0])} # sorting as per keys, since it is to be added to the dataframe
    scores_list = list(scores.values())
    rank  = {k: v for k, v in sorted(rank.items(), key=lambda item: item[0])} # sorting as per keys, since it is to be added to the dataframe
    rank_list = list(rank.values())

    for key in distance_top_keys:
        top_cities.append(cities[key])
        top_ids.append(ids[key])

    dff_1 = dff.copy()
    dff_1 = dff[(dff['city'].isin(top_cities)) & (dff['id'].isin(top_ids))]
    dff_1.insert(2, "score", scores_list)
    dff_1.insert(3, "rank", rank_list)

    return(dff_1)




app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.H1("City Search Tool", style={'text-align': 'center'}),

    html.Div(["Enter desired Home Price (in $)                                                                                                                                         ", dcc.Input(id='monthly_rent', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Cost of Living (in $)                                                                                                                                     ", dcc.Input(id='cost_of_living', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Internet Speed (in Mbps)                                                                                                                                   ", dcc.Input(id='internet_speed', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Population Desnity you would like to live in (per sq. miles)                                                                                               ", dcc.Input(id='pop_den', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Air Quality (in a scale of 1-10 with 10 being best and 1 being worst)                                                                                      ", dcc.Input(id='air_quality', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Traffic in the City (in a scale of 1-10 with 10 being heavy traffic and 1 being low traffic)                                                               ", dcc.Input(id='traffic_den', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Level of Safety in the City (in a scale of 1-10 with 10 being safest and 1 most unsafe)                                                                    ", dcc.Input(id='safety', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Walkability in the City (in a scale of 1-10 with 10 meaning everything in a walkable distance and 1 meaning you would need to drive everywhere)            ", dcc.Input(id='walking_grade', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter desired Pizza Rating in the City (in a scale of 1-5 with 5 meaning everything widely liked pizza and 1 meaning widely unliked pizza)                               ", dcc.Input(id='pizza', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter the average percent of graduates you would like in the City (between of 0 to 1)                                                                                    ",dcc.Input(id='graduate', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter the average percent of singles you would like in the City (between of 0 to 1)                                                                                      ",dcc.Input(id='single', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Enter the average percent of religious people you would like in the City (between of 0 to 1)                                                                             ",dcc.Input(id='religious', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Div(["Choose the political environment you would like in the City              ",dcc.Dropdown(id='politics', options = [{'label':i, 'value': i} for i in politics], value = 'Democrat')], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),

    html.Br(),
    html.Br(),
    html.Br(),

    html.Div(["How many cities would you like to rank (use natural numbers)                                                                            ",dcc.Input(id='num_rank', type='number', value=0.0)], style={'textAlign': 'left', 'color': colors['text'], 'font-size': '20px'}),
    html.Br(),
    html.Br(),

    #dcc.Input(placeholder = 'Enter Value 1', id='input-2-state', type='number', value=0.0),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit', style={'textAlign': 'center', 'color': colors['text'], 'font-size': '20px'}),

    dcc.Graph(id='map'),
])


@app.callback(Output(component_id='map', component_property='figure'),
              [Input('submit-button-state', 'n_clicks'),
              Input('politics','value')],
              [State('monthly_rent', 'value'),
               State('cost_of_living', 'value'),
               State('internet_speed', 'value'),
               State('pop_den', 'value'),
               State('air_quality', 'value'),
               State('traffic_den', 'value'),
               State('safety', 'value'),
               State('walking_grade', 'value'),
               State('pizza', 'value'),
               State('graduate', 'value'),
               State('single', 'value'),
               State('religious', 'value'),
               State('num_rank', 'value')])
def update_output(n_clicks, politics, rent, cost, internet, popden, air, traffic, safety_lev, walking, pizza_rating, graduates, singles, religion, rank_num):

    if(n_clicks == 0):
        raise PreventUpdate

    else:

        dff = rank_cities(politics, rent, cost, internet, popden, air, traffic, safety_lev, walking, pizza_rating, graduates, singles, religion, rank_num)

        fig = px.scatter_mapbox(dff, lat="lat", lon="lon", hover_name="city", hover_data=["state","score", "rank"],
                  color_discrete_sequence=["fuchsia"], zoom=3, height = 500)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})

        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
