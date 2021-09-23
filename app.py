# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import html
from dash import dcc
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd

df_bills = px.data.tips()
df_export = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')
df_life = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')


def generate_table(dataframe, max_rows=10):
    return html.Table([
                        html.Thead(
                            html.Tr([html.Th(col) for col in dataframe.columns])
                        ),
                        html.Tbody([
                            html.Tr([
                                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                            ]) for i in range(min(len(dataframe), max_rows))
                        ])
                    ])


app = dash.Dash(__name__)

fig_tips = px.strip(df_bills, x="total_bill", y="time", color="sex", title="Restaurants bills",
                    facet_col="day") # split to sub-plots

fig_life = px.scatter(df_life, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)

markdown_text = '''
                ### Dash and Markdown

                Dash apps can be written in Markdown.
                Dash uses the [CommonMark](http://commonmark.org/)
                specification of Markdown.
                Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
                if this is your first introduction to Markdown!
                '''


app.layout = html.Div(
                        children=[
                            html.H1(children='Hello Dash',
                                    style={'textAlign': 'center'}),
                            html.Div(children='Dash: A web application framework for your data', 
                                     style={'textAlign': 'center'}),
                            
                            dcc.Graph(id='example-graph',figure=fig_tips),
                            dcc.Graph(id='life-exp-vs-gdp',figure=fig_life),

                            dcc.Markdown(children=markdown_text),
                            
                            html.H1(children='US Agriculture Exports (2011)'),
                            generate_table(df_export),

                            html.H6("Change the value in the text box to see callbacks in action!"),
                            html.Div(["Input: ",dcc.Input(id='my-input', value='initial value', type='text')]),
                            html.Br(),
                            html.Div(id='my-output'),

                            
                            html.Label('Dropdown'),dcc.Dropdown(options=[
                                                                        {'label': 'New York City', 'value': 'NYC'},
                                                                        {'label': u'Montréal', 'value': 'MTL'},
                                                                        {'label': 'San Francisco', 'value': 'SF'}],
                                                                value='MTL'),
                            html.Label('Multi-Select Dropdown'),dcc.Dropdown(options=[
                                                                                    {'label': 'New York City', 'value': 'NYC'},
                                                                                    {'label': u'Montréal', 'value': 'MTL'},
                                                                                    {'label': 'San Francisco', 'value': 'SF'}],
                                                                            value=['MTL', 'SF'],
                                                                            multi=True),
                            html.Label('Radio Items'),dcc.RadioItems(options=[
                                                                            {'label': 'New York City', 'value': 'NYC'},
                                                                            {'label': u'Montréal', 'value': 'MTL'},
                                                                            {'label': 'San Francisco', 'value': 'SF'}],
                                                                    value='MTL'),
                            html.Label('Checkboxes'),dcc.Checklist(options=[
                                                                            {'label': 'New York City', 'value': 'NYC'},
                                                                            {'label': u'Montréal', 'value': 'MTL'},
                                                                            {'label': 'San Francisco', 'value': 'SF'}],
                                                                    value=['MTL', 'SF']),
                            html.Label('Text Input'),dcc.Input(value='MTL', type='text'),
                            html.Label('Slider'),dcc.Slider(min=0,max=9,
                                                    marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(1, 6)},
                                                    value=5)
                         ], # style={'columnCount': 2}
                        )

@app.callback( # for unput - output
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)

def update_output_div(input_value):
    return 'Output: {}'.format(input_value)


if __name__ == '__main__':
    app.run_server(debug=True) # automatic reloading
