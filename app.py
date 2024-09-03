from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

df_trigger = pd.read_csv('data/table_trigger.csv')
df_validation = pd.read_csv('data/table_validation.csv')



'''

TRANSFORMATIONS

'''
import pandas as pd

# Assuming df_trigger and df_validation are already defined and loaded

# Deduplicate triggers and standardize the 'tripped' and 'trigger' fields
df_trigger_dedup = df_trigger.drop_duplicates(subset=['account_canonical_id', 'run_datetime'])

# Merge the trigger and validation dataframes
merged_df = pd.merge(df_trigger_dedup, df_validation, on=['account_canonical_id', 'run_datetime'], how='left')
merged_df['account_tradeable'] = merged_df['account_tradeable'].apply(lambda x: 'TRUE' if x else 'FALSE')

# Calculate failure rates
merged_df['Failed'] = merged_df['account_tradeable'] == 'FALSE'

# Total counts per trigger
total_counts = merged_df['trigger'].value_counts().reset_index()
total_counts.columns = ['trigger', 'total_count']

# Failed counts per trigger
failed_counts = merged_df[merged_df['Failed']]['trigger'].value_counts().reset_index()
failed_counts.columns = ['trigger', 'failed_count']

# Merge counts and calculate percentages
table2 = pd.merge(failed_counts, total_counts, on='trigger')
table2['total_count'] = table2['total_count'] / 9
table2['failure_rate_percentage'] = (table2['failed_count'] / table2['total_count']) * 100
table2 = table2.sort_values(by='failure_rate_percentage', ascending=False)

print(table2)


'''

DASH COMPONENTS

'''
app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

items = [
    dbc.DropdownMenuItem("Excess cash"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Portfolio rebalance"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Withdrawal"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Liquidation")
]

app.layout = [
    html.H1(children='Order Generation Insights', style={'textAlign':'center'}),

    dbc.DropdownMenu(label="Trigger",
            size="lg",
            children=items,
            className="mb-3",id='dropdown-selection'),
    dcc.Graph(id='graph-content'),
    html.H2('By Samy Hachi')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'children'),
)
def update_graph(value):

    fig = go.Figure()
    fig.add_trace(go.Bar(x=table2['trigger'],
                         y=table2['failed_count'],
                         name='Count of Failed Validations',
                         marker_color='rgb(55, 83, 109)'
                         ))
    fig.add_trace(go.Bar(x=table2['trigger'],
                         y=table2['total_count'],
                         name='Count of Total Validations',
                         marker_color='rgb(26, 118, 255)'
                         ))

    fig.update_layout(
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
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',font = dict(color = '#FFFFFF')
)
    return fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
