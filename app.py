from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

# Assuming df_trigger and df_validation are loaded as shown above
df_trigger = pd.read_csv('data/table_trigger.csv')
df_validation = pd.read_csv('data/table_validation.csv')

# Data preprocessing and merging
df_trigger['tripped'] = df_trigger['tripped'].str.upper().str.strip().replace({'TRUE': True, 'FALSE': False})
df_trigger_dedup = df_trigger.drop_duplicates(subset=['account_canonical_id', 'run_datetime'])
merged_df = pd.merge(df_trigger_dedup, df_validation, on=['account_canonical_id', 'run_datetime'], how='left')
merged_df['account_tradeable'] = merged_df['account_tradeable'].apply(lambda x: 'TRUE' if x else 'FALSE')

# Prepare the data for all the tables as described in the previous parts
# Each table will be stored as a DataFrame named table1, table2, ..., table6

# For demonstration, using placeholders for table creation based on previous discussions
# Create these tables using pandas operations as previously detailed

# Placeholder data setup
table1 = merged_df.groupby('account_tradeable')['excess_cash_amount'].agg(['mean', 'count']).reset_index()
table2 = merged_df[merged_df['account_tradeable'] == 'FALSE'].groupby('trigger').size().reset_index(
    name='Failure Count')
table3 = merged_df.groupby(merged_df['run_datetime'].dt.hour).size().reset_index(name='Trigger Count')
table4 = merged_df.groupby('account_tradeable')['excess_cash_amount'].agg(['mean', 'count']).reset_index()
table5 = merged_df[['run_datetime', 'excess_cash_amount', 'trigger']].dropna(subset=['excess_cash_amount'])
table6 = merged_df[merged_df['account_tradeable'] == 'FALSE'].groupby('validation_category').agg(
    {'excess_cash_amount': ['mean', 'count']}).reset_index()

# Set up Dash app and layout
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

app.layout = html.Div([
    html.H1('Order Generation Insights', style={'textAlign': 'center'}),
    dbc.DropdownMenu(
        label="Select Analysis",
        children=[
            dbc.DropdownMenuItem("Table 1: Cash Utilization", id="table1"),
            dbc.DropdownMenuItem("Table 2: Trigger Failures", id="table2"),
            dbc.DropdownMenuItem("Table 3: Timing Analysis", id="table3"),
            dbc.DropdownMenuItem("Table 4: Account Performance", id="table4"),
            dbc.DropdownMenuItem("Table 5: Future Cash Excess", id="table5"),
            dbc.DropdownMenuItem("Table 6: Validation Failures", id="table6"),
        ],
        className="mb-3"
    ),
    dcc.Graph(id='graph-content')
])


@app.callback(
    Output('graph-content', 'figure'),
    Input('table1', 'n_clicks'),
    Input('table2', 'n_clicks'),
    Input('table3', 'n_clicks'),
    Input('table4', 'n_clicks'),
    Input('table5', 'n_clicks'),
    Input('table6', 'n_clicks'),
)
def update_graph(t1, t2, t3, t4, t5, t6):
    ctx = dash.callback_context

    if not ctx.triggered or ctx.triggered[0]['value'] is None:
        fig = go.Figure()
        fig.update_layout(title_text="Please select an analysis from the dropdown.")
        return fig

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "table1":
        fig = go.Figure(data=[
            go.Bar(name='Average Excess Cash', x=table1['account_tradeable'], y=table1['mean']),
            go.Bar(name='Total Accounts', x=table1['account_tradeable'], y=table1['count'])
        ])
        fig.update_layout(title_text='Impact of Validation Checks on Cash Utilization', barmode='group')
    elif button_id == "table2":
        fig = go.Figure(data=[
            go.Bar(x=table2['trigger'], y=table2['Failure Count'])
        ])
        fig.update_layout(title_text='Failure Rate by Trigger Type')
    elif button_id == "table3":
        fig = go.Figure(data=[
            go.Bar(x=table3['run_datetime'], y=table3['Trigger Count'])
        ])
        fig.update_layout(title_text='Timing Analysis for Trigger and Validation Activities')
    elif button_id == "table4":
        fig = go.Figure(data=[
            go.Bar(x=table4['account_tradeable'], y=table4['mean'], name='Average Excess Cash'),
            go.Bar(x=table4['account_tradeable'], y=table4['count'], name='Number of Transactions')
        ])
        fig.update_layout(title_text='Tradeable vs. Non-Tradeable Account Performance', barmode='group')
    elif button_id == "table5":
        fig = go.Figure(data=[
            go.Scatter(x=table5['run_datetime'], y=table5['excess_cash_amount'], mode='markers')
        ])
        fig.update_layout(title_text='Predictive Modeling for Future Cash Excess')
    elif button_id == "table6":
        fig = go.Figure(data=[
            go.Bar(x=table6['validation_category'], y=table6['excess_cash_amount']['mean'], name='Average Excess Cash'),
            go.Bar(x=table6['validation_category'], y=table6['excess_cash_amount']['count'], name='Count of Failures')
        ])
        fig.update_layout(title_text='Linking Account Features to Validation Failures', barmode='group')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8000)
