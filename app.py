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


# Table 1: Cash Utilization Insights
table1 = merged_df.groupby('account_tradeable')['excess_cash_amount'].agg(['mean', 'count']).reset_index()
table1.columns = ['Account Tradeable', 'Average Excess Cash', 'Total Accounts']

# Table 2: Trigger Failures Analysis
merged_df['Failed'] = merged_df['account_tradeable'] == 'FALSE'
total_counts = merged_df['trigger'].value_counts().reset_index()
total_counts.columns = ['trigger', 'total_count']
failed_counts = merged_df[merged_df['Failed']]['trigger'].value_counts().reset_index()
failed_counts.columns = ['trigger', 'failed_count']
table2 = pd.merge(failed_counts, total_counts, on='trigger')
table2['failure_rate_percentage'] = (table2['failed_count'] / table2['total_count']) * 100

# Table 4: Account Performance Analysis
table4 = merged_df.groupby('account_tradeable')['excess_cash_amount'].agg(['mean', 'count']).reset_index()
table4.columns = ['Account Tradeable', 'Average Excess Cash', 'Number of Transactions']

# Table 6: Validation Failures Analysis
filtered_df = merged_df[merged_df['account_tradeable'] == 'FALSE']
table6 = filtered_df.groupby('validation_category').agg(failure_count=('validation_category', 'count'),
                                                        avg_excess_cash=('excess_cash_amount', 'mean')).reset_index()
table6 = table6.sort_values(by='failure_count', ascending=False)

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
    fig1 = px.bar(table1, x='Account Tradeable', y='Average Excess Cash',
                  title='Average Excess Cash by Tradeable Status')

    # Graph for Table 2
    fig2 = px.bar(table2, x='trigger', y='failure_rate_percentage',
                  title='Trigger Failures and Their Rates', color='trigger')

    # Graph for Table 4
    fig3 = px.bar(table4, x='Account Tradeable', y='Average Excess Cash',
                  title='Account Performance by Tradeable Status')

    # Graph for Table 6
    fig4 = px.pie(table6, names='validation_category', values='failure_count',
                  title='Validation Failures by Category')

    # Add customization for each figure if necessary
    return [fig1, fig2, fig3, fig4]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)