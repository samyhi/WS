from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

# Assuming df_trigger and df_validation are loaded as shown above
df_trigger = pd.read_csv('data/table_trigger.csv')
df_validation = pd.read_csv('data/table_validation.csv')

# Data preprocessing and merging
df_trigger_dedup = df_trigger.drop_duplicates(subset=['account_canonical_id', 'run_datetime'])
merged_df = pd.merge(df_trigger_dedup, df_validation, on=['account_canonical_id', 'run_datetime'], how='left')
merged_df['account_tradeable'] = merged_df['account_tradeable'].apply(lambda x: 'TRUE' if x else 'FALSE')


table1 = merged_df.groupby('account_tradeable')['excess_cash_amount'].agg(['mean', 'count']).reset_index()
table2 = merged_df[merged_df['account_tradeable'] == 'FALSE'].groupby('trigger').size().reset_index(name='Failure Count')
table4 = merged_df.groupby('account_tradeable')['excess_cash_amount'].agg(['mean', 'count']).reset_index()
table6 = merged_df[merged_df['account_tradeable'] == 'FALSE'].groupby('validation_category').agg({'excess_cash_amount': ['mean', 'count']}).reset_index()

# Prepare the data for all the tables as described in previous parts
# Each table will be stored as a DataFrame named table1, table2, ..., table6
# Create these tables using pandas operations as previously detailed

# Set up Dash app and layout
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    html.H1('Order Generation Insights', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='analysis-dropdown',
        options=[
            {'label': 'Table 1: Cash Utilization', 'value': 'table1'},
            {'label': 'Table 2: Trigger Failures', 'value': 'table2'},
            {'label': 'Table 4: Account Performance', 'value': 'table4'},
            {'label': 'Table 6: Validation Failures', 'value': 'table6'}
        ],
        value='table1',
        style={'width': '50%'}
    ),
    dcc.Graph(id='graph-content')
])

@app.callback(
    Output('graph-content', 'figure'),
    [Input('analysis-dropdown', 'value')]
)
def update_graph(selected_table):
    if selected_table == "table1":
        fig = go.Figure(data=[
            go.Bar(name='Average Excess Cash', x=table1['account_tradeable'], y=table1['mean']),
            go.Bar(name='Total Accounts', x=table1['account_tradeable'], y=table1['count'])
        ])
        fig.update_layout(title_text='Impact of Validation Checks on Cash Utilization', barmode='group')
    elif selected_table == "table2":
        fig = go.Figure(data=[
            go.Bar(x=table2['trigger'], y=table2['Failure Count'])
        ])
        fig.update_layout(title_text='Failure Rate by Trigger Type')
    elif selected_table == "table4":
        fig = go.Figure(data=[
            go.Bar(x=table4['account_tradeable'], y=table4['mean'], name='Average Excess Cash'),
            go.Bar(x=table4['account_tradeable'], y=table4['count'], name='Number of Transactions')
        ])
        fig.update_layout(title_text='Tradeable vs. Non-Tradeable Account Performance', barmode='group')
    elif selected_table == "table6":
        fig = go.Figure(data=[
            go.Bar(x=table6['validation_category'], y=table6['excess_cash_amount']['mean'], name='Average Excess Cash'),
            go.Bar(x=table6['validation_category'], y=table6['excess_cash_amount']['count'], name='Count of Failures')
        ])
        fig.update_layout(title_text='Linking Account Features to Validation Failures', barmode='group')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8000)
