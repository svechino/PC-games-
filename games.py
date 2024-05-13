#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table, dcc
import dash_bootstrap_components as dbc


# In[2]:


import plotly.express as px


# In[3]:


data = pd.read_csv('games.csv')
data.head()


# In[4]:


data.describe()


# In[5]:


df = data[data['Year_of_Release'] >= 2000]
df.head()


# In[6]:


df['Year_of_Release'] = df['Year_of_Release'].astype(int)


# In[7]:


df=df.dropna()


# In[8]:


df['User_Score'] = df['User_Score'].apply(pd.to_numeric, errors='coerce').fillna(0, downcast='infer')


# In[9]:


df.info()


# In[10]:


df['Rating'].unique()


# In[11]:


dict_age_rate = {'E':0, 'M':17, 'T':13, 'E10+':10, 'AO':18, 'RP':17}
df.replace({"Rating":dict_age_rate}, inplace=True)


# E - Все
# Е 10+ – Все в возрасте 10+
# T - подросток
# M – Зрелые (17+)
# A – Взрослый (только 18+)
# RP - Ожидается рейтинг
# RP (вероятно для взрослых 17+) – Оценка ожидается, но контент, скорее всего, предназначен для людей старше 17 лет.

# In[12]:


df['Platform'].unique()


# In[13]:


app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
app.layout = dbc.Container([
    dbc.Row([
        html.H1('Game Market Analysis', style={'textAlign':'center','color':'green'})
    ], style={'marginTop': '20px', 'marginBottom': '20px'}), 
    dbc.Row([
        dcc.Markdown('Feel free to interact with the dropdown menus and the year range slider to explore different aspects of the game market data.', style={'textAlign':'left'})
    ], style={'marginTop': '20px', 'marginBottom': '20px'}),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='platform_filter',
                options=[{'label': platform, 'value': platform} for platform in df['Platform'].unique()],
                multi=True, 
                placeholder='Select a platform'
            )
        ]), 
        dbc.Col([
            dcc.Dropdown(
                id='genre_filter', 
                options=[{'label': genre, 'value': genre} for genre in df['Genre'].unique()],
                multi=True,
                placeholder='Select a genre'
            )
        ]), 
        dbc.Col([
            dcc.RangeSlider(
                min=2000, max=2020, step=5, value=[2010, 2020], 
                marks={2000: '2000', 2005: '2005', 2010: '2010', 2015: '2015', 2020: '2020'},
                id='year_slider'
            )
        ])
    ], style={'marginTop': '20px', 'marginBottom': '20px'}), 
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(children='Total games released', style={'textAlign':'center'}), 
                    html.H4(id='total_games', children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
            ])
        ]), 
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(children='Average players score', style={'textAlign':'center'}), 
                    html.H4(id='players_score', children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
            ])
        ]), 
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(children='Average critics score', style={'textAlign':'center'}), 
                    html.H4(id='critics_score', children="", style={'fontWeight':'bold', 'textAlign':'center'})
                ])
            ])
        ])
    ]), 
    dbc.Row([
        dbc.Col([
            dcc.Graph(id = 'stack_area_plot', figure = {})
        ]), 
        dbc.Col([
            dcc.Graph(id = 'scatter_plot', figure = {})
        ]), 
        dbc.Col([
            dcc.Graph(id = 'rating_genre', figure = {})
        ])
    ])
], fluid = True)

# Total games card
@app.callback(
    Output('players_score', 'children'),
    Output('total_games', 'children'),
    Output('critics_score', 'children'),
    Input('platform_filter', 'value'),
    Input('genre_filter', 'value'),
    Input('year_slider', 'value')
)
def filter_data(chosen_platform, chosen_genre, year_range):
    dff = df
    if chosen_platform:
        dff = dff[dff['Platform'].isin(chosen_platform)]
    if chosen_genre:
        dff = dff[dff['Genre'].isin(chosen_genre)]
        
    # year_slider filtering
    dff = dff[(dff['Year_of_Release'] >= year_range[0]) & (dff['Year_of_Release'] <= year_range[1])]
    
    players_score = dff['User_Score'].mean()
    critic_score = dff['Critic_Score'].mean()
    total_games = dff['Name'].count()
    critic_score_rounded = round(critic_score, 2)  # Round to 2 decimal places
    players_score_rounded = round(players_score, 2)
    return players_score_rounded, total_games, critic_score_rounded

# Graphs
@app.callback(
    Output('stack_area_plot', 'figure'),
    Output('scatter_plot', 'figure'),
    Output('rating_genre', 'figure'),
    Input('platform_filter', 'value'),
    Input('genre_filter', 'value'),
    Input('year_slider', 'value')
)
def update_stacked_area_plot(chosen_platform, chosen_genre, year_range):
    dff = df
    if chosen_platform:
        dff = dff[dff['Platform'].isin(chosen_platform)]
    if chosen_genre:
        dff = dff[dff['Genre'].isin(chosen_genre)]
    dff = dff[(dff['Year_of_Release'] >= year_range[0]) & (dff['Year_of_Release'] <= year_range[1])]
    
    # Area stacked graph total games by platform by year
    area_stacked = dff.groupby(['Year_of_Release', 'Platform'])['Name'].count().reset_index()
    fig1 = px.area(area_stacked, x='Year_of_Release', y='Name', color='Platform', line_group='Platform')
    fig1.update_layout(
        title='Total Games Amount by Platfrom Over the Years',
        xaxis_title = 'Years of Release',
        yaxis_title = 'Games Number')
    
    # Scatter plot users & critics score by genre
    scatter = dff[dff['User_Score']!=0]
    fig2 = px.scatter(scatter, x="User_Score", y="Critic_Score", color="Genre")
    fig2.update_layout(
        title='Users Score vs. Critic Score by Genre',
        xaxis_title = 'Users Score',
        yaxis_title = 'Critics Score')
     
    # line chart for rating by genre
    rating_by_genre = dff.groupby(['Year_of_Release', 'Genre'])['Rating'].mean().reset_index()
    fig3 = px.line(rating_by_genre, x='Year_of_Release', y='Rating', color='Genre')
    fig3.update_layout(
        title='Average User Rating by Genre Over the Years',
        xaxis_title = 'Years of Release',
        yaxis_title = 'Average Age Rating')
    
    return fig1, fig2, fig3

if __name__=='__main__':
    app.run_server(debug=True, port=8054)

