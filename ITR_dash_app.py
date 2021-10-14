# Run this app with `python ITR_dash_app.py` and
# visit http://127.0.0.1:8050/ in your web browser
# and pray.


import pandas as pd
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

import ITR
from ITR.data.excel import ExcelProvider
from ITR.portfolio_aggregation import PortfolioAggregationMethod
from ITR.temperature_score import TemperatureScore
from ITR.interfaces import ETimeFrames, EScope

# Initial calculations
import pathlib
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
# default_study_data = pd.read_csv(DATA_PATH.joinpath("study.csv"))
provider = ExcelProvider(path="data/data_provider_example.xlsx")
df_portfolio = pd.read_csv("data/example_portfolio_main.csv", encoding="iso-8859-1", sep=';')
companies = ITR.utils.dataframe_to_portfolio(df_portfolio)
temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],scopes=[EScope.S1S2],aggregation_method=PortfolioAggregationMethod.WATS) # Options for the aggregation method are WATS, TETS, AOTS, MOTS, EOTS, ECOTS, and ROTS
amended_portfolio_global = temperature_score.calculate(data_providers=[provider], portfolio=companies)
all_columns = list(amended_portfolio_global.columns)
amended_portfolio_short=amended_portfolio_global[['company_name', 'time_frame', 'scope', 'temperature_score']]
aggregated_score = temperature_score.aggregate_scores(amended_portfolio_global).long.S1S2.all.score
sectors = amended_portfolio_global["sector"].unique()
regions = amended_portfolio_global["region"].unique()

df = pd.DataFrame(
    {
        "First Name": ["Arthur", "Ford", "Zaphod", "Trillian"],
        "Last Name": ["Dent", "Prefect", "Beeblebrox", "Astra"]
    })


intro_text = """
**About this app**
This app applies [ITR](http://insideairbnb.com/get-the-data.html) blabla. sdsdv d sd sdvsv svdvds
ssdvvsv sd sdvsd ffdv fvdfvd fs vsdfvsdv sdv
"""

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ITR Tool"
server = app.server



# simple_jumbotron = dbc.Jumbotron(
#     [
#         html.H1("Jumbotron", className="display-3"),
#         html.P(
#             "Use a jumbotron to call attention to "
#             "featured content or information.",
#             className="lead",
#         ),
#         html.Hr(className="my-2"),
#         html.P(
#             "Jumbotrons use utility classes for typography and "
#             "spacing to suit the larger container."
#         ),
#         html.P(dbc.Button("Learn more", color="primary"), className="lead"),
#     ]
# )

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
                        # min=amended_portfolio.cumulative_budget.min(),max=amended_portfolio.cumulative_budget.max(),
                        # value=[amended_portfolio.cumulative_budget.min(), amended_portfolio.cumulative_budget.max()],
                        min = 0, max = 1000, value=[0,1000],
                        step=50,
                        marks={i: str(i) for i in range(0, 1000, 200)},
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
                    dcc.Dropdown(id="sector-dropdown",options=[{"label": i, "value": i} for i in sectors],placeholder="Select a sector"),            
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
                    dcc.Dropdown(id="region-dropdown",options=[{"label": i, "value": i} for i in regions],placeholder="Select a region"),            
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
                    dcc.Dropdown(id="scenario-dropdown",options=[{"label": i, "value": i} for i in sectors],placeholder="Select emission scenario"),            
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
                    dcc.Store(id='memory-output'),
                    # simple_jumbotron,
                    html.Div(
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
                    dbc.Row(
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
                            # dcc.Upload(
                            #     id='upload-data',
                            #     children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
                            #     style={'width': '100%','height': '60px','lineHeight': '60px',
                            #         'borderWidth': '1px','borderStyle': 'dashed','borderRadius': '5px',
                            #         'textAlign': 'center','margin': '10px'},
                            #     multiple=False # Allow multiple files to be uploaded
                            # ),
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                    [
                        dbc.Col([

                            dbc.Card(dbc.CardBody(
                                                [
                                                    html.H5("Portfolio filters", className="pf-filter"),
                                                    html.P("Here you could select part of your portfolio"),
                                                    controls,
                                                    dbc.Button("Reset filters", color="secondary",size="sm"),
                                                ]
                                            )
                                    ),     
                            html.Br(),
                            dbc.Card(dbc.CardBody(
                                                [
                                                    html.H5("Macro assumptions", className="macro-filters"),
                                                    html.P("Here you could adjust bacis assumptions of calculations"),
                                                    macro,
                                                    dbc.Button("Reset to default", color="secondary",size="sm"),
                                                ]
                                            )
                                    ),       
                                ],
                            width=3,
                        ),
                        dbc.Col([
                                dbc.Row([
                                        dbc.Col(
                                            dbc.Card(dbc.CardBody(
                                                                [
                                                                    html.H1(id="output-info"),
                                                                    html.P('This is cumulative temperature score of a selected portfolio'),
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
                                        dbc.Col(
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
                                        dbc.Col(
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
                                dbc.Row([dbc.Col(dcc.Graph(id="graph-2"),)
                                    ],
                                ),
                                dbc.Row([
                                    dbc.Col(dcc.Graph(id="graph-3", 
                                                      # style={"height": "70vh", "max-height": "90vw",'title': 'Dash Data Visualization'},
                                              ),
                                    ),
                                    dbc.Col(dcc.Graph(id="graph-4", 
                                                    # style={"height": "70vh", "max-height": "90vw",'title': 'Dash Data Visualization'},
                                            ),
                                    ),
                                ]),
                                dbc.Row([
                                    dbc.Card(dbc.CardBody(
                                                        [
                                                            html.H5("Portfolio filters", className="pf-filter"),
                                                            # dbc.Table.from_dataframe(
                                                            #     df=pd.DataFrame(),
                                                            #     id="container-button-basic",
                                                            #     striped=True,
                                                            #     bordered=True,
                                                            #     hover=True,
                                                            #     responsive=True,
                                                            # ),                                                            
                                                            # html.Div(id='container-button-basic'),
                                                            # dbc.Table.from_dataframe(amended_portfolio_global[amended_portfolio_global.columns[:5]], 
                                                            #                          # striped=True, bordered=True, hover=True,
                                                            # ),                      
                                                          ],
                                                        #   id="container-button-basic",
                                                    ),
                                            ),     

                                    # dbc.Button('Table', id='table-but', n_clicks=0),
                                    # html.Div(id='container-button-basic'),
                                    # html.Table(id='output-data-upload'),

                                    # html.Div(id='output-data-upload'),
                                    # dash_table.DataTable(id='output-data-upload'),
                                    # dash_table.DataTable(id='output-data-upload',
                                    #                     columns=[{'name': i, 'id': i} for i in amended_portfolio_short.columns],
                                    #                     editable=False,
                                    # ),
                                ]),

                            ]
                        ),
                    ]
                    )
                ],
            style={"max-width": "1500px", "margin": "auto"},
            )



# Tables -----------------------------------------------
    
    # def make_dash_table(df):
    #     """ Return a dash definition of an HTML table for a Pandas dataframe """
    #     table = []
    #     for index, row in df.iterrows():
    #         html_row = []
    #         for i in range(len(row)):
    #             html_row.append(html.Td([row[i]]))
    #         table.append(html.Tr(html_row))
    #     return table

    # def generate_table(dataframe, max_rows=26):
    #     return html.Table(
    #         # Header
    #         [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
    #         # Body
    #         [html.Tr([
    #             html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
    #         ]) for i in range(min(len(dataframe), max_rows))]
    #     )


    # def generate_table(dataframe, max_rows=10):
    #     return html.Table([
    #         html.Thead(
    #             html.Tr([html.Th(col) for col in dataframe.columns])
    #         ),
    #         html.Tbody([
    #             html.Tr([
    #                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
    #             ]) for i in range(min(len(dataframe), max_rows))
    #         ])
    #     ])


    # # return html Table with dataframe values
    # def df_to_table(df):
    #     return html.Table(
    #         [html.Tr([html.Th(col) for col in df.columns])]
    #         + [
    #             html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
    #             for i in range(len(df))
    #         ]
    #     )
    



@app.callback(
    [
    Output("graph-2", "figure"), 
    Output("graph-3", "figure"), 
    Output("graph-4", "figure"), 
    Output('output-info','children'),
    Output('comp-info','children'),
    Output('indu-info','children'),
    # Output('container-button-basic', 'children'),
    # Output('output-data-upload', 'data'),
    # Output('output-data-upload', 'columns'),
    ],

    [
#        Input('memory-output', 'data'), # here is our imported csv in memory
        Input("carb-budg", "value"), 
        Input("temp-score", "value"),
        # Input('table-but', 'n_clicks'),
        Input("run-url", "n_clicks"), 
        Input("input-url", "n_submit"),
        # Input("sector-dropdown", "value"), # commented out for later implementation
        # Input("region-dropdown", "value"), # commented out for later implementation
    ],
    [State("input-url", "value")],

)

def update_graph(
                # df_store,
                ca_bu, 
                te_sc, 
                # table_click,
                n_clicks, n_submit, url,
                #  sec, reg,
                 ):

    global amended_portfolio_global

    if n_clicks is None:
        # raise PreventUpdate
        amended_portfolio = amended_portfolio_global
        carbon_mask = (amended_portfolio.cumulative_budget >= ca_bu[0]) & (amended_portfolio.cumulative_budget <= ca_bu[1])
        # filt_df = amended_portfolio.loc[carbon_mask]
        temp_score_mask = (amended_portfolio.temperature_score >= te_sc[0]) & (amended_portfolio.temperature_score <= te_sc[1])
        filt_df = amended_portfolio.loc[carbon_mask & temp_score_mask]
        # sec_reg_mask = (amended_portfolio.sector == sec & amended_portfolio.region == reg)
        # filt_df = amended_portfolio.loc[carbon_mask & temp_score_mask & sec_reg_mask]
        # filt_df = amended_portfolio.copy()
        amended_portfolio_global = filt_df
        temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],scopes=[EScope.S1S2],aggregation_method=PortfolioAggregationMethod.WATS)
        aggregated_score = temperature_score.aggregate_scores(filt_df).long.S1S2.all.score
    else:
    # if df_store is None:
    #     raise PreventUpdate
        df_portfolio = pd.read_csv(url, encoding="iso-8859-1", sep=';')
        companies = ITR.utils.dataframe_to_portfolio(df_portfolio)
        temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],scopes=[EScope.S1S2],aggregation_method=PortfolioAggregationMethod.WATS) # Options for the aggregation method are WATS, TETS, AOTS, MOTS, EOTS, ECOTS, and ROTS
        amended_portfolio = temperature_score.calculate(data_providers=[provider], portfolio=companies)
        # amended_portfolio = pd.from_dict(data, orient='index',columns=all_columns)
        # amended_portfolio = pd.read_json(df_store, orient='split')
        carbon_mask = (amended_portfolio.cumulative_budget >= ca_bu[0]) & (amended_portfolio.cumulative_budget <= ca_bu[1])
        # filt_df = amended_portfolio.loc[carbon_mask]
        temp_score_mask = (amended_portfolio.temperature_score >= te_sc[0]) & (amended_portfolio.temperature_score <= te_sc[1])
        filt_df = amended_portfolio.loc[carbon_mask & temp_score_mask]
        amended_portfolio_global = filt_df
        # sec_reg_mask = (amended_portfolio.sector == sec & amended_portfolio.region == reg)
        # filt_df = amended_portfolio.loc[carbon_mask & temp_score_mask & sec_reg_mask]
        # filt_df = amended_portfolio.copy()
        aggregated_score = temperature_score.aggregate_scores(filt_df).long.S1S2.all.score


    # Create a plotly.express scatter plot
    fig1 = px.scatter(filt_df, x="cumulative_target", y="cumulative_budget", size="temperature_score", 
                    color = "sector", labels={"color": "Sector"}, title="Overview of portfolio")
    fig1.update_layout(transition_duration=500)
    fig2 = px.scatter(filt_df, x="sector", y="region", size="temperature_score", title = "Industry vs Region ratings")
    fig2.update_layout(transition_duration=500)
    fig3 = px.bar(filt_df.query("temperature_score > 2"), x="company_name", y="temperature_score", text ="temperature_score", color="sector",title="Worst contributors")
    fig3.update_layout(transition_duration=500)

    out_msg = f"{aggregated_score:.2f}"
    # filt_df_short=filt_df[['company_name', 'time_frame', 'scope', 'temperature_score']].reset_index().head()

    return (
        fig1, fig2, fig3,
        out_msg, str(len(filt_df)), str(len(filt_df.sector.unique())),
        # dbc.Table.from_dataframe(filt_df_short),
    )


    #, dbc.Table.from_dataframe(filt_df[filt_df.columns[:4]].head(5))

    # return dbc.Table.from_dataframe(filt_df_short)
    
    
    # dash_table.DataTable(
    #                                         id='table',
    #                                         columns=[{'name': i, 'id': i} for i in filt_df.columns],
    #                                         data=filt_df.to_dict('rows'),
    #                                         style_cell={'width': '300px','height': '60px','textAlign': 'left'})

    # generate_table(filt_df)
    
    #         # filt_df.to_dict(orient='records'), [{'name': str(i), 'id': str(i)} for i in filt_df.columns]
            

# @app.callback(
#     Output('container-button-basic', 'children'),
#     [Input('table-but', 'n_clicks')])

# def search_fi(n_clicks):
#     if n_clicks > 0:
#         df = pd.DataFrame(
#          {
#              "First Name": ["Arthur", "Ford", "Zaphod", "Trillian"],
#              "Last Name": ["Dent", "Prefect", "Beeblebrox", "Astra"]
#          })
#         # print(df)
#         return dbc.Table.from_dataframe(df)



# Calculate different weighting methods
# def agg_score(agg_method):
#     temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],scopes=[EScope.S1S2],aggregation_method=agg_method) # Options for the aggregation method are WATS, TETS, AOTS, MOTS, EOTS, ECOTS, and ROTS
#     amended_portfolio = temperature_score.calculate(data_providers=[provider], portfolio=companies)
#     aggregated_scores = temperature_score.aggregate_scores(amended_portfolio)
#     return [agg_method.value,aggregated_scores.long.S1S2.all.score]

# agg_temp_scores = [agg_score(i) for i in PortfolioAggregationMethod]
# fig_compare_weight = px.bar(pd.DataFrame(agg_temp_scores), x=0, y=1, text=1, title = "Comparing of different weighting methods applied to portfolio")




'''
# Reading csv from url
@app.callback(
    [
        Output('memory-output', 'data'),
    ],

    [Input("run-url", "n_clicks"), 
    Input("input-url", "n_submit")],
    
    [State("input-url", "value")],
)
def run_model(n_clicks, n_submit, url):

    df_portfolio = pd.read_csv(url, encoding="iso-8859-1", sep=';')
    companies = ITR.utils.dataframe_to_portfolio(df_portfolio)
    temperature_score = TemperatureScore(time_frames = [ETimeFrames.LONG],scopes=[EScope.S1S2],aggregation_method=PortfolioAggregationMethod.WATS) # Options for the aggregation method are WATS, TETS, AOTS, MOTS, EOTS, ECOTS, and ROTS
    amended_portfolio = temperature_score.calculate(data_providers=[provider], portfolio=companies)
    return amended_portfolio.to_json(orient='split')

'''




# file upload function
# def parse_contents(contents, filename):
#     content_type, content_string = contents.split(',')
#     decoded = base64.b64decode(content_string)
#     if 'csv' in filename:
#         # Assume that the user uploaded a CSV file
#         df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
#     elif 'xls' in filename:
#         # Assume that the user uploaded an excel file
#         df = pd.read_excel(io.BytesIO(decoded))
#     return df

# @app.callback(Output('memory-output', 'data'),
#               [Input('upload-data', 'contents'),
#                Input('upload-data', 'filename')])
# def update_output(contents, filename):
#     if contents is not None:
#         data_df = parse_contents(contents, filename)
#         if data_df is not None:
#             return data_df.to_json(orient='split')
#         else:
#             return [{}]
#     else:
#         return [{}]






if __name__ == "__main__":
    app.run_server(debug=True)