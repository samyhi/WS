from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots


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
    html.H1("Dashboard: Insights from Order Generation", style={'textAlign': 'center'}),
    html.H3('For: WealthSimple Managed Investing Team, By: Samy Hachi', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph1'), width=6),
        dbc.Col(dcc.Graph(id='graph2'), width=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph3'), width=6),
        dbc.Col(dcc.Graph(id='graph4'), width=6),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=1*60*1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)

@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('graph3', 'figure'),
     Output('graph4', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(_):
    # Create each figure using Plotly Express or Graph Objects
    # Graph for Table 2
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(go.Bar(x=table2['trigger'],
                          y=table2['failed_count'],
                          name='Count of Failed Validations',
                          marker_color='rgb(55, 83, 109)'
                          ), secondary_y=False)
    fig2.add_trace(go.Bar(x=table2['trigger'],
                          y=table2['total_count'] / 9,
                          name='Count of Total Validations',
                          marker_color='rgb(26, 118, 255)'
                          ), secondary_y=False)

    fig2.add_trace(go.Scatter(x=table2['trigger'],
                              y=table2['failure_rate_percentage'],
                              name='Validation Failure Rate',
                              marker_color='red'
                              ), secondary_y=True)

    fig2.update_layout(
        title='Relationship triggers/validation outcomes',
        xaxis_tickfont_size=14,
        yaxis=dict(
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.1  # gap between bars of the same location coordinate.
    )
    fig2.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', font=dict(color='#FFFFFF'))
    fig2.update_yaxes(title_text="Number of validation tests", secondary_y=False)
    fig2.update_yaxes(title_text="Percentage of failure", secondary_y=True)

    fig1 = px.bar(table1, x='Account Tradeable', y='Average Excess Cash',
                  title='Average Excess Cash by Tradeable Status')
    fig1.update_traces(marker_color='red')
    fig1.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', font=dict(color='#FFFFFF'))


    # Graph for Table 4
    fig3 = px.bar(table4, x='Account Tradeable', y='Average Excess Cash',
                  title='Account Performance by Tradeable Status')
    fig3.update_traces(marker_color='green')
    fig3.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', font=dict(color='#FFFFFF'))

    # Graph for Table 6
    fig4 = px.pie(table6, names='validation_category', values='failure_count',
                  title='Validation Failures by Category')
    fig4.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', font=dict(color='#FFFFFF'))
    # Add customization for each figure if necessary
    return [fig2, fig1, fig3, fig4]

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)