import json
from six.moves.urllib.parse import quote

import advertools as adv
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd


app = dash.Dash()
server= app.server

app.layout = html.Div([
    html.Br(), html.Br(),
    html.Div('Search Engine Marketing: Keyword Generation Tool',
             style={'text-align': 'center', 'font-size': 30}),
    html.Br(), html.Br(),
    html.Div([
        html.Div([

            html.Content('Edit campaign name:'),
            dcc.Input(id='campaign_name',
                      value='SEM_Campaign',
                      style={'height': 35, 'width': '97%', 'font-size': 20, 
                             'font-family': 'Palatino'}),
            html.Br(), html.Br(),
            html.Content('Select match type(s):'),
            dcc.Dropdown(id='match_types',
                         multi=True,
                         options=[{'label': match, 'value': match}
                                  for match in ['Exact', 'Phrase', 'Modified', 'Broad']],
                         value=['Exact', 'Phrase']),
            html.Br(),
            dcc.Checklist(id='order_matters',
                          values=[True],
                          options=[{'label': 'Order matters', 'value': True}]),

            html.Br(), html.Br(),
            html.Div([
                html.Div([
                    html.Content(' Products:'),
                    dcc.Textarea(id='products_table', value='', rows=20,
                                 placeholder='Products you sell, one per line\n'
                                 'Example:\n\nhonda\ntoyota\nbmw\netc...',
                                 style={'font-size': 16}),
                ], style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    html.Content(' Words:'),
                    dcc.Textarea(id='words_table', value='', rows=20,
                                 placeholder='Words that signify purchase intent, one per line\n'
                                 'Example:\n\nbuy\nprice\nshop\netc...',
                                 style={'font-size': 16}),
                ], style={'width': '30%', 'display': 'inline-block', 'float': 'right'}),
            ])
        ], style={'width': '20%', 'display': 'inline-block', 'font-family': 'Palatino',
                  'margin-left': '2%'}),
        html.Div([
            html.Button(id='submit', children='Generate Keywords', n_clicks=0,
                        style={'height': 30, 'background-color': '#C6EAFF',
                               'border-radius': '12px', 'font-size': 18}),
            html.Br(), html.Br(),
            dt.DataTable(id='output_df',
                         editable=False,
                         sortable=True,
                         filterable=False,
                         max_rows_in_viewport=10,
                         columns=['Campaign', 'Ad Group', 'Keyword', 'Criterion Type', 'Labels'],
                         rows=adv.kw_generate([''], [''], match_types=['Broad']).to_dict('records')),
            html.Br(),
            html.A('Download Keywords',
                   id='download_link',
                   download="rawdata.csv",
                   href="",
                   target="_blank"),
            html.Div(id='kw_df_summary', style={'width': '80%','margin-left': '5%'})
        ], style={'width': '60%', 'display': 'inline-block', 'float': 'right',
                  'margin-right': '5%', 'font-family': 'Palatino'}),
    ]),
    html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), 
], style={'background-color': '#eeeeee', 'font-family': 'Palatino'})

@app.callback(Output('kw_df_summary', 'children'),
             [Input('output_df', 'rows')])
def display_kw_df_summary(kw_df_list):
    kw_df = pd.DataFrame(kw_df_list)
    return [html.H3('Summary:'),
            html.Content('Total keywords: ' + str(len(kw_df))), html.Br(),
            html.Content('Unique Keywords: ' + str(kw_df['Keyword'].nunique())), html.Br(),
            html.Content('Ad Groups: ' + str(kw_df['Ad Group'].nunique())),
            html.Br(), html.Br(),
            html.Content('For more details on the logic behind generating the keywords,'
                         'please checkout the '),
            html.A('DataCamp tutorial on Search Engine Marketing.',
                   href='http://bit.ly/datacamp_sem'), html.Br(), html.Br(),
            html.Content('Functionality based on the '), 
            html.A('advertools', href='http://bit.ly/advertools'), html.Content(' package.')]

@app.callback(Output('output_df', 'rows'),
             [Input('submit', 'n_clicks')],
             [State('products_table', 'value'),
              State('words_table', 'value'),
              State('match_types', 'value'),
              State('campaign_name', 'value'),
              State('order_matters', 'values')])
def generate_kw_df(button, products, words, match_types, campaign_name, order_matters):
    if products and words:
        product_list = list({x.strip() for x in products.split('\n') if x})
        if '' in product_list:
            product_list.remove('')
        word_list = list({x.strip() for x in words.split('\n')})

        return adv.kw_generate(product_list, word_list, 
                               match_types=match_types,
                               order_matters=bool(order_matters),
                               campaign_name=campaign_name).to_dict('records')

@app.callback(Output('download_link', 'href'),
             [Input('output_df', 'rows')])
def download_df(data_df):
    df = pd.DataFrame.from_dict(data_df, 'columns')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)
    return csv_string

@app.callback(Output('submit', 'hidden'),
             [Input('products_table', 'value'),
              Input('words_table', 'value'),
              Input('match_types', 'value'),
              Input('campaign_name', 'value')])
def show_submit_button(products, words, match_types, campaign_name):
    if products and words and match_types and campaign_name:
        return False
    return True


if __name__ == '__main__':
    app.run_server()