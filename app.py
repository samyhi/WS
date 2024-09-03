from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
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
server = app.server
app.layout = dbc.Container([
    html.H1("Dashboard: Insights into Order Generation", style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph1'), width=6),
        dbc.Col(dcc.Graph(id='graph2'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph3'), width=6),
        dbc.Col(dcc.Graph(id='graph4'), width=6),
    ])
], fluid=True)

@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('graph3', 'figure'),
     Output('graph4', 'figure')],
    [Input('app-loading', 'children')]
)
def update_graphs(_):
    # Create each figure using Plotly Express or Graph Objects
    fig1 = px.bar(merged_df, x='account_tradeable', y='excess_cash_amount', title="Table 1: Cash Utilization Insights")
    fig2 = px.scatter(merged_df, x='trigger', y='excess_cash_amount', color='account_tradeable', title="Table 2: Trigger Failures")
    fig3 = px.histogram(merged_df, x='account_tradeable', y='excess_cash_amount', title="Table 4: Account Performance")
    fig4 = px.pie(merged_df, names='validation_category', title="Table 6: Validation Failures")

    # Add customization for each figure if necessary
    return [fig1, fig2, fig3, fig4]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)