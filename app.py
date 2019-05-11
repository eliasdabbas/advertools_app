import base64

from six.moves.urllib.parse import quote

import advertools as adv
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash_table import DataTable
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import logging

img_base64 = base64.b64encode(open('./logo.png', 'rb').read()).decode('ascii')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s==%(funcName)s==%(message)s')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

server = app.server

app.layout = html.Div([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Img(src='data:image/png;base64,' + img_base64, width=200),
            html.A(['online marketing', html.Br(), 'productivity & analysis'],
                   href='https://github.com/eliasdabbas/advertools')
        ], sm=12, lg=2, style={'text-align': 'center'}), html.Br(),
        dbc.Col([
            html.H2('Search Engine Marketing: Keyword Generation Tool',
                    style={'text-align': 'center'}),
        ], sm=12, lg=9),
    ], style={'margin-left': '5%'}),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Label('Edit campaign name:'),
            dbc.Input(id='campaign_name',
                      value='SEM_Campaign'),
            html.Br(),
            dbc.Label('Select match type(s):'),
            dcc.Dropdown(id='match_types',
                         multi=True,
                         options=[{'label': match, 'value': match}
                                  for match in ['Exact', 'Phrase', 'Modified',
                                                'Broad']],
                         value=['Exact', 'Phrase']),
            html.Br(),
            dbc.Checklist(id='order_matters',
                          values=['True'],
                          options=[{'label': 'Order matters', 'value': 'True'}]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Label(' Products:'),
                    dbc.Textarea(id='products_table', value='', rows=20,
                                 cols=10,
                                 placeholder='Products you sell, one per line\n'
                                 'Example:\n\nhonda\ntoyota\nbmw\netc...')
                ]),
                dbc.Col([
                    dbc.Label(' Words:'),
                    dbc.Textarea(id='words_table', value='', rows=20,
                                 cols=10,
                                 placeholder='Words that signify purchase intent, '
                                 'one per line\n'
                                 'Example:\n\nbuy\nprice\nshop\netc...'),
                ]),
            ])
        ], sm=11, lg=3, style={'margin-left': '5%'}),
        dbc.Col(lg=1),
        dbc.Col([
            dbc.Button(id='submit', children='Generate Keywords',
                       style={'display': 'none'}),
            html.Br(), html.Br(),
            dcc.Loading(
                DataTable(id='output_df',
                          virtualization=True,
                          n_fixed_rows=1,
                          style_cell={'width': '150px'},
                          columns=[{'name': col, 'id': col}
                                   for col in ['Campaign', 'Ad Group',
                                               'Keyword', 'Criterion Type',
                                               'Labels']]),
            ),
            html.Br(),
            html.A('Download Keywords',
                   id='download_link',
                   download="rawdata.csv",
                   href="",
                   target="_blank",
                   n_clicks=0),
            html.Div(id='kw_df_summary')
        ], sm=11, lg=7),
    ] + [html.Br() for x in range(10)]),
    html.Div(id='download')
], style={'background-color': '#eeeeee'})


@app.callback(Output('kw_df_summary', 'children'),
              [Input('output_df', 'data')])
def display_kw_df_summary(kw_df_list):
    kw_df = pd.DataFrame(kw_df_list)
    return [html.H3('Summary:'),
            html.Content('Total keywords: ' + str(len(kw_df))), html.Br(),
            html.Content('Unique Keywords: ' + str(kw_df['Keyword'].nunique())),
            html.Br(),
            html.Content('Ad Groups: ' + str(kw_df['Ad Group'].nunique())),
            html.Br(), html.Br(),
            html.Content('For more details on the logic behind generating '
                         'the keywords, please checkout the '),
            html.A('DataCamp tutorial on Search Engine Marketing.',
                   href='http://bit.ly/datacamp_sem'), html.Br(), html.Br(),
            html.Content('Functionality based on the '),
            html.A('advertools', href='http://bit.ly/advertools'),
            html.Content(' package.')]


@app.callback(Output('output_df', 'data'),
              [Input('submit', 'n_clicks')],
              [State('products_table', 'value'),
               State('words_table', 'value'),
               State('match_types', 'value'),
               State('campaign_name', 'value'),
               State('order_matters', 'values')])
def generate_kw_df(button, products, words, match_types, campaign_name,
                   order_matters):
    if any([x is None for x in [button, products, words, match_types,
                                campaign_name, order_matters]]):
        raise PreventUpdate
    if button and products and words and match_types and campaign_name:
        logging.info(msg=locals())

    if products and words:
        product_list = list({x.strip() for x in products.split('\n') if x})
        if '' in product_list:
            product_list.remove('')
        word_list = list({x.strip() for x in words.split('\n')})
        final_df = adv.kw_generate(product_list, word_list,
                               match_types=match_types,
                               order_matters=bool(order_matters[0]),
                               campaign_name=campaign_name)
        return final_df.to_dict('rows')

@app.callback(Output('download_link', 'href'),
              [Input('output_df', 'data')])
def download_df(data_df):
    df = pd.DataFrame.from_dict(data_df, 'columns')
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)
    return csv_string


@app.callback(Output('download', 'children'),
              [Input('download_link', 'n_clicks')])
def register_file_downloads(n_clicks):
    if n_clicks:
        logging.info(str(n_clicks) + '_file_download')


@app.callback(Output('submit', 'style'),
              [Input('products_table', 'value'),
               Input('words_table', 'value'),
               Input('match_types', 'value'),
               Input('campaign_name', 'value')])
def show_submit_button(products, words, match_types, campaign_name):
    if products is None and words is None:
        raise PreventUpdate
    if products and words:
        return {'display': 'inline'}


if __name__ == '__main__':
    app.run_server()
