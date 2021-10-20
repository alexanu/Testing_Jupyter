# Run this app with `python ITR_dash_app.py` and
# visit http://127.0.0.1:8050/ in your web browser
# and pray.


import pandas as pd
import os
import base64
import datetime
import io

import dash
from dash import html
from dash import dcc
from dash import dash_table

import dash_bootstrap_components as dbc # should be installed separately


from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go

import ITR
from ITR.data.excel import ExcelProviderCompany, ExcelProviderProductionBenchmark, ExcelProviderIntensityBenchmark
from ITR.data.data_warehouse import DataWarehouse
from ITR.portfolio_aggregation import PortfolioAggregationMethod
from ITR.temperature_score import TemperatureScore
from ITR.interfaces import ETimeFrames, EScope

print(ITR.__path__)


# Initial calculations
print('Start!!!!!!!!!')

directory1 = '' #'examples'
directory2="data"
company_database = 'test_data_company.xlsx'
benchm_data = 'OECM_EI_and_production_benchmarks.xlsx'
dummy_portfolio = "example_portfolio.csv"
# dummy_portfolio = "example_portfolio_test.csv"

excel_company_data = ExcelProviderCompany(excel_path=os.path.join(directory1,directory2,company_database))
excel_production_bm = ExcelProviderProductionBenchmark(excel_path=os.path.join(directory1,directory2,benchm_data))
excel_EI_bm = ExcelProviderIntensityBenchmark(excel_path=os.path.join(directory1,directory2,benchm_data),benchmark_temperature=1.5,benchmark_global_budget=396, is_AFOLU_included=False)
excel_provider = DataWarehouse(excel_company_data, excel_production_bm, excel_EI_bm)
df_portfolio = pd.read_csv(os.path.join(directory1,directory2,dummy_portfolio), encoding="iso-8859-1", sep=';')
print('got till here 1')
companies = ITR.utils.dataframe_to_portfolio(df_portfolio)
temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],scopes=[EScope.S1S2],aggregation_method=PortfolioAggregationMethod.WATS) # Options for the aggregation method are WATS, TETS, AOTS, MOTS, EOTS, ECOTS, and ROTS
amended_portfolio_global = temperature_score.calculate(data_warehouse=excel_provider, portfolio=companies)
initial_portfolio = amended_portfolio_global
sectors = initial_portfolio["sector"].unique()
regions = initial_portfolio["region"].unique()
print('got till here 2')


intro_text = """
**About this app**
This app applies [ITR](http://insideairbnb.com/get-the-data.html) blabla. sdsdv d sd sdvsv svdvds
ssdvvsv sd sdvsd ffdv fvdfvd fs vsdfvsdv sdv
"""

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ITR Tool"
server = app.server

controls = dbc.Row(
    [
        dbc.Col(
         children=[   
            dbc.FormGroup(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("\N{scroll} Benchmark carbon budget"), 
                                width=9,
                                ),
                            dbc.Col(
                                [
                                dbc.Button("\N{books}",id="hover-target1", color="link", n_clicks=0),
                                dbc.Popover(dbc.PopoverBody("And here's some amazing content. Cool!"),id="hover1",target="hover-target1",trigger="hover"), 
                                ], width=2,
                                ),                           
                        ],
                        align="center",
                    ),
                    dcc.RangeSlider(
                        id="carb-budg",
                        min=initial_portfolio.cumulative_budget.min(),max=initial_portfolio.cumulative_budget.max(),
                        value=[initial_portfolio.cumulative_budget.min(), initial_portfolio.cumulative_budget.max()],
                        tooltip={'always_visible': True, 'placement': 'bottom'},
                        step=10**9,
                        marks=dict((i/(10**9),str(i/(10**9))) for i in range(0, 10**10, 10**9)),

                        
                    ),
                ]
            ),
            dbc.FormGroup(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("\N{thermometer} Individual temperature score"), 
                                width=9,
                                ),
                            dbc.Col(
                                [
                                dbc.Button("\N{books}",id="hover-target2", color="link", n_clicks=0),
                                dbc.Popover(dbc.PopoverBody("And here's some amazing content. Cool!"),id="hover2",target="hover-target2",trigger="hover"), 
                                ], width=2, align="center",
                                ),                           
                        ],
                        align="center",
                    ),
                    dcc.RangeSlider(
                        id="temp-score",
                        # min=amended_portfolio.temperature_score.min(),max=amended_portfolio.temperature_score.max(),
                        # value=[amended_portfolio.temperature_score.min(), amended_portfolio.temperature_score.max()],
                        min = 0, max = 3, value=[0,3],
                        step=0.5,
                        marks={i / 10: str(i / 10) for i in range(0, 30, 5)},
                    ),
                ]
            ),
            dbc.FormGroup(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("\N{factory} Focus on a specific sector "), 
                                width=9,
                                ),
                            dbc.Col(
                                [
                                dbc.Button("\N{books}",id="hover-target3", color="link", n_clicks=0),
                                dbc.Popover(dbc.PopoverBody("And here's some amazing content. Cool!"),id="hover3",target="hover-target3",trigger="hover"), 
                                ], width=2,
                                ),                           
                        ],
                        align="center",
                    ),
                    dcc.Dropdown(id="sector-dropdown",
                                options=[{"label": i, "value": i} for i in sectors] + [{'label': 'All Sectors', 'value': 'all_values'}],
                                 value = 'all_values',
                                 clearable =False,
                                 placeholder="Select a sector"),            
                ]
            ),
            dbc.FormGroup(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("\N{globe with meridians} Focus on a specific region "), 
                                width=9,
                                ),
                            dbc.Col(
                                [
                                dbc.Button("\N{books}",id="hover-target4", color="link", n_clicks=0),
                                dbc.Popover(dbc.PopoverBody("And here's some amazing content. Cool!"),id="hover4",target="hover-target4",trigger="hover"), 
                                ], width=2,
                                ),                           
                        ],
                        align="center",
                    ),
                    dcc.Dropdown(id="region-dropdown",
                                 options=[{"label": i, "value": i} for i in regions] + [{'label': 'All Regions', 'value': 'all_values'}],
                                 value = 'all_values',
                                 clearable =False,
                                 placeholder="Select a region"),            
                ]
            ),            
         ],
        ),
    ],
)

macro = dbc.Row(
    [
        dbc.Col(
         children=[   
            dbc.FormGroup(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("\N{bar chart} Select Benchmark "), 
                                width=9,
                                ),
                            dbc.Col(
                                [
                                dbc.Button("\N{books}",id="hover-target5", color="link", n_clicks=0),
                                dbc.Popover(dbc.PopoverBody("And here's some amazing content. Cool!"),id="hover5",target="hover-target5",trigger="hover"), 
                                ], width=2,
                                ),                           
                        ],
                        align="center",
                    ),                    
                    dcc.Dropdown(id="scenario-dropdown",
                                options=[{"label": i, "value": i} for i in ['OECM-1.5','NGFS']],
                                value='OECM-1.5',
                                clearable =False,
                                placeholder="Select emission scenario"),            
                ]
            ),
            dbc.FormGroup(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Label("\N{game die} Assumed GDP growth "), 
                                width=9,
                                ),
                            dbc.Col(
                                [
                                dbc.Button("\N{books}",id="hover-target6", color="link", n_clicks=0),
                                dbc.Popover(dbc.PopoverBody("And here's some amazing content. Cool!"),id="hover6",target="hover-target6",trigger="hover"), 
                                ], width=2,
                                ),                           
                        ],
                        align="center",
                    ),                      
                    dcc.Dropdown(id="gdp_fc",options=[{"label": i, "value": i} for i in regions],placeholder="Select GDP growth"),            
                ]
            ),            
         ],
        ),
    ],
)

# Define Layout
app.layout = dbc.Container(
                children=[
                    dcc.Store(id='memory-output'), # not used, but the idea is to use as clipboard to store dataframe
                    html.Div( # banner
                        children=[
                            # Change App Name here
                            html.Div(
                                className="container scalable",
                                children=[
                                    # Change App Name here
                                    html.H1(id="banner-title",children=[html.A("ITR Tool",href="https://github.com/plotly/dash-svm",style={"text-decoration": "none","color": "inherit"})]),
                                    html.Div(children='Calculation of temperature score for the provided portfolio of financial instruments \N{deciduous tree}'),
                                    # html.Div(id="intro-text", children=dcc.Markdown(intro_text)),
                                    # html.A(id="banner-logo",children=[html.Img(src=app.get_asset_url("dash-logo-new.png"))],href="https://plot.ly/products/dash/"),
                                    ]
                                )
                            ]
                        ),
                    html.Hr(),
                    dbc.Row( # upload portfolio
                        [

                            dbc.Col(
                                [dbc.InputGroup(
                                            [dbc.InputGroupAddon("Put the URL of a csv portfolio here:", addon_type="prepend"),
                                            dbc.Input(
                                                id="input-url",
                                                value = 'data/example_portfolio_main.csv',
                                                # placeholder='data/example_portfolio_main.csv',
                                                ),
                                            ]
                                    ),
                                ],
                                width = 9,
                            ),
                            dbc.Col(dbc.Button("Upload new portfolio", id="run-url", color="primary", block=True, ),   
                                    width=3,
                            ),                         
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                    [
                        dbc.Col([ # filters pane

                            dbc.Card(dbc.CardBody(
                                                [
                                                    html.H5("Portfolio filters", className="pf-filter"),
                                                    html.P("Here you could select part of your portfolio"),
                                                    controls,
                                                    dbc.Button("Reset filters", id="reset-filters-but", color="secondary",size="sm"),
                                                ]
                                            )
                                    ),     
                            html.Br(),
                            dbc.Card(dbc.CardBody(
                                                [
                                                    html.H5("Macro assumptions", className="macro-filters"),
                                                    html.P("Here you could adjust bacis assumptions of calculations"),
                                                    macro,
                                                ]
                                            )
                                    ),       
                                ],
                            width=3,
                        ),
                        dbc.Col([
                                dbc.Row([ # Row with key figures
                                        dbc.Col( # PF score
                                            dbc.Card(dbc.CardBody(
                                                                [
                                                                    html.H1(id="output-info"),
                                                                    html.P('This is cumulative temperature score of a selected portfolio'),
                                                                ]
                                                            )
                                                    ),       
                                            # width=2,
                                            ),
                                        dbc.Col( # Number of companies
                                            dbc.Card(dbc.CardBody(
                                                                [
                                                                    html.H1(id="comp-info"),
                                                                    html.P('Number of companies in the selected portfolio'),
                                                                    # html.Div(id="output-info"),

                                                                    # dbc.FormGroup([
                                                                    #         dbc.Label("Carbon budget of individual holdings"),
                                                                    #         html.H2(["Example heading", dbc.Badge("New")]),
                                                                    #         dbc.Label("Carbon budget of individual holdings"),
                                                                    #         dbc.Label("Carbon budget of individual holdings"),
                                                                    #     ]),
                                                                ]
                                                            )
                                                    ),       
                                            # width=2,
                                            ),
                                        dbc.Col( # Number of industries
                                            dbc.Card(dbc.CardBody(
                                                                [
                                                                    html.H1(id="indu-info"),
                                                                    html.P('Number of industries in the selected portfolio'),
                                                                    # html.Div(id="output-info"),

                                                                    # dbc.FormGroup([
                                                                    #         dbc.Label("Carbon budget of individual holdings"),
                                                                    #         html.H2(["Example heading", dbc.Badge("New")]),
                                                                    #         dbc.Label("Carbon budget of individual holdings"),
                                                                    #         dbc.Label("Carbon budget of individual holdings"),
                                                                    #     ]),
                                                                ]
                                                            )
                                                    ),       
                                            # width=2,
                                            ),                                                                                        
                                    ],
                                ),
                                dbc.Row([dbc.Col(dcc.Graph(id="graph-2"),) # big bubble graph
                                    ],
                                ),
                                dbc.Row([ # 2 graphs
                                    dbc.Col(dcc.Graph(id="graph-3", 
                                                      # style={"height": "70vh", "max-height": "90vw",'title': 'Dash Data Visualization'},
                                              ),
                                    ),
                                    dbc.Col(dcc.Graph(id="graph-4", 
                                                    # style={"height": "70vh", "max-height": "90vw",'title': 'Dash Data Visualization'},
                                            ),
                                    ),
                                ]),
                                dbc.Row([ # 2 graphs
                                    dbc.Col(dcc.Graph(id="graph-5", 
                                                      # style={"height": "70vh", "max-height": "90vw",'title': 'Dash Data Visualization'},
                                              ),
                                    ),
                                ]),                                
                                dbc.Row([ # Table
                                    dbc.Button("Show members of a selected portfolio",id="table-but",color="primary",n_clicks=0),
                                ]),
                                html.Br(),
                                dbc.Card(dbc.CardBody(
                                        [
                                        # html.H5("Portfolio filters"),
                                        html.Div(id='container-button-basic'),
                                        ]
                                        ),
                                ),

                            ]
                        ),
                    ]
                    )
                ],
            style={"max-width": "1500px", "margin": "auto"},
            )
print('got till here 4')


@app.callback(
    [
    Output("graph-2", "figure"), 
    Output("graph-3", "figure"), 
    Output("graph-4", "figure"), 
    Output("graph-5", "figure"), 
    Output('output-info','children'), # portfolio score
    Output('output-info','style'), # conditional color
    Output('comp-info','children'), # num of companies
    Output('indu-info','children'), # num of industries
    Output('carb-budg', 'min'), Output('carb-budg', 'max'), 
    # Output('temp-score', 'min'), Output('temp-score', 'max'),

    ],

    [
#        Input('memory-output', 'data'), # here is our imported csv in memory
        Input("carb-budg", "value"), 
        Input("temp-score", "value"),
        # Input('table-but', 'n_clicks'),
        Input("run-url", "n_clicks"), 
        Input("input-url", "n_submit"),
        Input("sector-dropdown", "value"), 
        Input("region-dropdown", "value"),
    ],
    [State("input-url", "value")],
)

def update_graph(
                # df_store,
                ca_bu, 
                te_sc, 
                # table_click,
                n_clicks, n_submit, 
                sec, reg,
                url,
                ):

    global amended_portfolio_global, initial_portfolio, temperature_score

    print('got till here 5')

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] # to catch which widgets were pressed
    if 'run-url' in changed_id: # if "upload new pf" button was clicked
        df_portfolio = pd.read_csv(url, encoding="iso-8859-1", sep=';')
        companies = ITR.utils.dataframe_to_portfolio(df_portfolio)
        initial_portfolio = temperature_score.calculate(data_warehouse=excel_provider, portfolio=companies)
        filt_df = initial_portfolio
        amended_portfolio_global = filt_df
        aggregated_scores = temperature_score.aggregate_scores(filt_df)

    else: # no new portfolio
        carbon_mask = (initial_portfolio.cumulative_budget >= ca_bu[0]) & (initial_portfolio.cumulative_budget <= ca_bu[1])
        temp_score_mask = (initial_portfolio.temperature_score >= te_sc[0]) & (initial_portfolio.temperature_score <= te_sc[1])

        # Dropdown filters
        if sec == 'all_values':
            sec_mask = (initial_portfolio.sector != 'dummy') # select all
        else:
            sec_mask = initial_portfolio.sector == sec
        if reg == 'all_values':
            reg_mask = (initial_portfolio.region != 'dummy') # select all
        else:
            reg_mask = (initial_portfolio.region == reg)
        filt_df = initial_portfolio.loc[carbon_mask & temp_score_mask & sec_mask & reg_mask] # filtering
        if len(filt_df) == 0: # if after filtering the dataframe is empty
            raise PreventUpdate
        amended_portfolio_global = filt_df
        aggregated_scores = temperature_score.aggregate_scores(filt_df) # calc temp score for companies left in pf


    # Calculate different weighting methods
    def agg_score(agg_method):
        temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],
                                             scopes=[EScope.S1S2],
                                             aggregation_method=agg_method) # Options for the aggregation method are WATS, TETS, AOTS, MOTS, EOTS, ECOTS, and ROTS
        aggregated_scores = temperature_score.aggregate_scores(filt_df)
        return [agg_method.value,aggregated_scores.long.S1S2.all.score]

    agg_temp_scores = [agg_score(i) for i in PortfolioAggregationMethod]
    df_temp_score = pd.DataFrame(agg_temp_scores)
    # Separate column for names on Bar chart
    Weight_Dict = {'WATS': 'Investment<Br>weighted', # <Br> is needed to wrap x-axis label
                'TETS': 'Total emissions<Br>weighted', 
                'EOTS': "Enterprise Value<Br>weighted", 
                'ECOTS': "Enterprise Value<Br>+ Cash weighted", 
                'AOTS': "Total Assets<Br>weighted", 
                'ROTS': "Revenues<Br>weigted",
                'MOTS': 'Market Cap<Br>weighted'}
    df_temp_score['Weight_method'] = df_temp_score[0].map(Weight_Dict) # Mapping code to text
    df_temp_score[1]=df_temp_score[1].round(decimals = 2)
    # Creating barchart
    fig4 = px.bar(df_temp_score, x='Weight_method', y=1, text=1,title = "Comparing of different weighting methods applied to portfolio")
    fig4.add_hline(y=2, line_dash="dot",line_color="red",annotation_text="Critical value") # horizontal line
    fig4.update_traces(textposition='inside', textangle=0)
    fig4.update_yaxes(title_text='Temperature score', range = [1,3])
    fig4.update_xaxes(title_text=None, tickangle=0)
    fig4.update_layout(transition_duration=500)


    # Scatter plot
    fig1 = px.scatter(filt_df, x="cumulative_target", y="cumulative_budget", size="temperature_score", 
                    color = "sector", labels={"color": "Sector"}, title="Overview of portfolio")
    fig1.update_layout(transition_duration=500)
    

    # Heatmap
    trace = go.Heatmap(
                    x = filt_df.sector,
                    y = filt_df.region,
                    z = filt_df.temperature_score,
                    type = 'heatmap',
                    colorscale = 'Temps',
                    )
    data = [trace]
    fig2 = go.Figure(data = data)
    fig2.update_layout(title = "Industry vs Region ratings")


    fig3 = px.bar(filt_df.query("temperature_score > 2"), 
                    x="company_name", y="temperature_score", 
                    text ="temperature_score",
                    color="sector",title="Worst contributors")
    fig3.update_traces(textposition='inside', textangle=0)
    fig3.update_yaxes(title_text='Temperature score', range = [1,4])
    fig3.update_layout(xaxis_title = None,transition_duration=500)


    drop_d_min = initial_portfolio.cumulative_budget.min()
    drop_d_max = initial_portfolio.cumulative_budget.max()

    return (
        fig1, fig2, fig3, fig4,
        "{:.2f}".format(aggregated_scores.long.S1S2.all.score), # portfolio score
        {'color': 'ForestGreen'} if aggregated_scores.long.S1S2.all.score < 2 else {'color': 'Red'}, # conditional color
        str(len(filt_df)), str(len(filt_df.sector.unique())), # num of companies and sectors in pf
        drop_d_min, drop_d_max, 
    )

@app.callback( # reseting dropdowns
    [
    Output("carb-budg", "value"),
    Output("temp-score", "value"),
    Output("sector-dropdown", "value"),
    Output("region-dropdown", "value"),
    ],
    [Input('reset-filters-but', 'n_clicks')]
)

def reset_filters(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return ( # if button is clicked, reset filters
        [initial_portfolio.cumulative_budget.min(), initial_portfolio.cumulative_budget.max()],
        [0,3],
        'all_values',
        'all_values',
    )

@app.callback( # showing table
    Output('container-button-basic', 'children'),
    [Input('table-but', 'n_clicks')])

def search_fi(n_clicks):
    if n_clicks > 0: # if button is clicked
        df=amended_portfolio_global[['company_name', 'company_id','region','sector','cumulative_budget','investment_value','temperature_score']]
        df['temperature_score']=df['temperature_score'].round(decimals = 2) # formating column
        df['cumulative_budget'] = df['cumulative_budget'].apply(lambda x: "${:,.1f} Mn".format((x/1000000))) # formating column
        df['investment_value'] = df['investment_value'].apply(lambda x: "${:,.1f} Mn".format((x/1000000))) # formating column
        df = df.sort_values(by='temperature_score', ascending=False)
        return dbc.Table.from_dataframe(df,
                                        striped=True,
                                        bordered=True,
                                        hover=True,
                                        responsive=True,
                                    )                                                          



if __name__ == "__main__":
    app.run_server(debug=True)