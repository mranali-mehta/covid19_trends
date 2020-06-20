#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver 
from bs4 import BeautifulSoup
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import re


# In[2]:


def setup_env():
    chromedriver = './tmp/chromedriver'
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    browser = webdriver.Chrome(executable_path = chromedriver, chrome_options = options)
    return browser

def scrape_web(browser, web_url):
    browser.get(web_url)
    requiredHtml = browser.page_source
    soup = BeautifulSoup(requiredHtml, 'html5lib')
    return soup

def extract_table(table):
    my_table = table[0]
    rows = my_table.findChildren(['th','tr'])
    final_list = []
    for row in rows:
        cells = row.findChildren('td')
        val_list = []
        for cell in cells:
            value = cell.text
            val_list.append(value)
        final_list.append(val_list)
    china_df = pd.DataFrame(final_list[1:],columns = final_list[0])

    country_list = ['Japan', 'South Korea', 'Singapore', 'United States', 'United Kingdom', 'Australia', 'Hong Kong', 
                   'Iran', 'Iraq', 'Italy', 'Thailand', 'Malaysia', 'Germany', 'France', 'Canada', 'Taiwan', 'TOTAL']

    my_table = table[1]
    rows = my_table.findChildren(['th','tr'])
    final_list = []
    for row in rows:
        cells = row.findChildren('td')
        val_list = []
        for cell in cells:
            value = cell.text
            val_list.append(value)
        if len(final_list) == 0:
            final_list.append(val_list)
        if val_list[0] in country_list:
            final_list.append(val_list)
    other_country_df = pd.DataFrame(final_list[1:], columns = final_list[0])
    
    return [china_df, other_country_df]
        
    


# In[11]:


def trending_data():
    # Trends Data
    country_list = ['China','Japan','South Korea', 'Singapore', 'United States', 'United Kingdom', 'Australia', 'Worldwide']
    country_dict = dict()
    for country in country_list:
        cntry = country.lower().replace(" ","")
        filename = "corona_" + cntry + ".csv"
        df = pd.read_csv(filename, skiprows = 2)
        df = df.drop(df.index[range(0,30)])
        df = df.reset_index(drop = True)
        country_dict[country] = df
    return country_dict
#trends_data = trending_data()
#trends_data.keys()
#trends_data.values()


# In[12]:


def dashboard(china_df, other_country_df, trends_data):
    app = dash.Dash()
    trends_country = ['China','Japan','South Korea', 'Singapore', 'United States', 'United Kingdom', 'Australia', 'Worldwide']

    colors = {
        'screen':'#D3D3D3',
        'background': '#111111',
        'text': '#7FDBFF',
        'dropdown':'orange'
    }

    app.layout = html.Div(style={'rows':2, 'backgroundColor':colors['background']}, children=[ 
        html.Div(style={'color':colors['text'], 'textAlign':'center'},children=[
            html.H1(children="Corona Virus Trends in different Parts of the World"),

            html.Div(style={'columns':2}, children=[
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id = 'country-trends',
                            options = [{'label': i, 'value': i} for i in trends_country],
                            value = 'China'
                        )
                ],style={'color': colors['text'],'width':'50%','display':'inline-block'})
            ]),

            html.H2(id='title1', style={
                'textAlign': 'center',
                'color': colors['text']
            }),
            dcc.Graph(id='Trends', style={
                'textAlign': 'center',
                'color': colors['text'],
                'backgroundColor': colors['background']
            }),

            html.Div([
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id = 'country-info',
                            options = [{'label': i, 'value': i} for i in ['China', 'World']],
                            value = 'China'
                        )
                ],style={'color': colors['text'], 'width':'50%','display':'inline-block'})
                ]),

                html.H2(id='title2', 
                    style={'textAlign': 'center',
                        'color': colors['text'],
                        'display':'inline-block'}),

                html.Div(style={'columns':2}, children = [
                    dcc.Graph(id='Info-1', style={
                        'textAlign': 'center',
                        'color': colors['text'],
                        'backgroundColor': colors['background']
                    }),

                    dcc.Graph(id='Info-2', style={
                        'textAlign': 'center',
                        'color': colors['text'],
                        'backgroundColor': colors['background']
                    })

                    ])
                ])
            ]),
            html.Div(style = {'color':colors['text']}, children=[
                    html.H3(id='Wuhan',
                      style={'textAlign': 'center',
                         'align':'between',
                        'color': colors['dropdown'],
                        'display':'inline-block'})
                        ])
        ])
    ])    


    @app.callback(
        Output('title1','children'),
        [Input('country-trends','value')]
    )
    def title1_text(country):
        return "Trends of Covid19 - " + country


    @app.callback(
        Output('Trends','figure'),
        [Input('country-trends','value')]
    )
    def update_graphTrends(country):
        df = trends_data[country]
        y_val = 'Coronavirus: (' + country + ')'
        return {
            'data': [{'x':df['Day'], 'y':df[y_val], 'type':'line'}],
            
            'layout':{
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }

    @app.callback(
        Output('title2','children'),
        [Input('country-info','value')]
    )
    def title2_text(country):
        return "Information of Covid19 in " + country


    @app.callback(
        Output('Info-1', 'figure'),
        [Input('country-info', 'value')]
    )
    def update_graphInfo1(country):
        if country == 'China':
            df = china_df
            x_val = df['MAINLAND CHINA'][1:-1]
            y_val = df['Cases'][1:-1]

            figure_value = {
            'data': [
                        {'x': x_val, 'y': y_val, 'type': 'bar', 'name': 'Cases'}
                    ],
                'layout':{
                    'title':'Number of Cases',
                        'plot_bgcolor': colors['background'],
                        'paper_bgcolor': colors['background'],
                        'font': {
                            'color': colors['text']
                            }
                        }
            }

        else:
            df = other_country_df
            x_val = df['OTHER PLACES'][:-1]
            y_val = df['Cases'][:-1]
            figure_value = {
                'data': [
                        {'x': x_val, 'y': y_val, 'type': 'bar', 'name': 'Cases'}
                    ],
                'layout':{
                    'title':'Number of Cases',
                        'margin':dict(l=50, r=50, t=50, b=50),
                        'plot_bgcolor': colors['background'],
                        'paper_bgcolor': colors['background'],
                        'font': {
                            'color': colors['text']
                            }
                        }
            }

        return figure_value



    @app.callback(
        Output('Info-2', 'figure'),
        [Input('country-info', 'value')]
    )
    def update_graphInfo2(country):
        if country == 'China':
            df = china_df
            x_val = df['MAINLAND CHINA'][1:-1]
            y_val = df['Deaths'][1:-1]

            figure_value = {
            'data': [
                        {'x': x_val, 'y': y_val, 'type': 'bar', 'name': 'Deaths'},
                    ],
                'layout':{
                    'title':'Number of Deaths',
                        'plot_bgcolor': colors['background'],
                        'paper_bgcolor': colors['background'],
                        'font': {
                            'color': colors['text']
                            }
                        }
            }

        else:
            df = other_country_df
            x_val = df['OTHER PLACES'][:-1]
            y_val = df['Deaths'][:-1]

            figure_value = {
                'data': [
                        {'x': x_val, 'y': y_val, 'type': 'bar', 'name': 'Deaths'},
                    ],
                'layout':{
                    'title':'Number of Deaths',
                        'margin':dict(l=50, r=50, t=50, b=50),
                        'plot_bgcolor': colors['background'],
                        'paper_bgcolor': colors['background'],
                        'font': {
                            'color': colors['text']
                            }
                        }
            }

        return figure_value

    @app.callback(
        Output('Wuhan','children'),
        [Input('country-info','value')]
    )
    def title2_text(country):
        if country == 'China':
            info = china_df[0:1].values
            text = info[0][0]
            text = text + "<=>    Cases = " + info[0][1]
            text = text + "<=>    Deaths = " + info[0][2]
            text = text + "<=>     " + info[0][3]
        else:
            info = other_country_df[-1:].values
            text = "World " + info[0][0]
            text = text + "<=>    Cases = " + info[0][1]
            text = text + "<=>    Deaths = " + info[0][2]
            text = text + "<=>     " + info[0][3]
        return text
    return app



# In[13]:


def main():
    #import_dependencies()
    browser = setup_env()
    web_url = "https://bnonews.com/index.php/2020/02/the-latest-coronavirus-cases/"
    soup = scrape_web(browser, web_url)
    
    table = soup.findChildren('table')
    table_content = extract_table(table)
    china_df = table_content[0]
    other_country_df = table_content[1]
    
    trends_data = trending_data()
    
    app = dashboard(china_df, other_country_df, trends_data)
    server = app.server
    app.run_server(debug=False)
    


# In[14]:


if __name__ == '__main__':
    main()
    
    
# In[ ]:




