import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import warnings
import webbrowser
from threading import Timer
import os

warnings.filterwarnings('ignore')


df = pd.read_csv('activities_cleaned.csv')

# pandas trata as datas como texto e não consegue realizar operações baseadas em tempo, como agrupar por semana ou mês.
df['Activity date'] = pd.to_datetime(df['Activity date'])

# Definindo a coluna 'Activity date' como o índice do DataFrame.
df.set_index('Activity date', inplace=True)

# Calculando os valores para os KPIs.
total_corridas = len(df)
total_distancia = df['Distance'].sum()
total_minutos_corridos = df['Moving Time Minutos'].sum()

# Formatando o tempo total para horas e minutos para melhor visualização
total_horas = int(total_minutos_corridos // 60)
minutos_restantes = int(total_minutos_corridos % 60)
tempo_formatado = f'{total_horas}h{minutos_restantes}m'

# Gráfico 1: Distância corrida por semana
distancia_semana = df['Distance'].resample('W-SUN').sum().reset_index()
distancia_semana.columns = ['Semana', 'Distância']
fig_distancia_semana = px.bar(
    distancia_semana,
    x='Semana',
    y='Distância',
    labels={"Semana": "Semana (Início no Domingo)", "Distância": "Distância Total (km)"},
    title="Distância corrida por Semana",
    color_discrete_sequence=['#FC4C02'],
)
fig_distancia_semana.update_layout(
    title_x=0.5,
    xaxis_title="Período de Treino",
    yaxis_title="Distância Total (km)",
    plot_bgcolor='#C0C0C0'
)
fig_distancia_semana.update_xaxes(dtick="M1", tickformat="%d %b\n%Y")


# Gráfico 2: Total de minutos corridos por semana
minutos_semana = df['Moving Time Minutos'].resample('W-SUN').sum().reset_index()
minutos_semana.columns = ['Semana', 'Tempo_minutos']
fig_minutos_semana = px.line(
    minutos_semana,
    x='Semana',
    y='Tempo_minutos',
    title='Total de Minutos Corridos por Semana',
    labels={"Semana": "Data", "Tempo_minutos": "Minutos Corridos na Semana"},
    color_discrete_sequence=['#FC4C02']
)
fig_minutos_semana.update_xaxes(rangeslider_visible=True)
fig_minutos_semana.update_layout(
    title_x=0.5,
    xaxis_title="Período de Treino",
    yaxis_title="Tempo Total (minutos)",
    plot_bgcolor='#C0C0C0'
)

# Gráfico 3: Total de dias corridos por mês
dias_por_mes = df.resample('ME').size().reset_index()
dias_por_mes.columns = ['Mês', 'Dias']
dias_por_mes['Mês'] = dias_por_mes['Mês'].dt.strftime('%b %Y')
fig_dias_por_mes = px.bar(
    dias_por_mes,
    x='Mês',
    y='Dias',
    title="Total de Dias Corridos por Mês",
    labels={"Mês": "Mês", "Dias": "Quantidade de Dias"},
    color_discrete_sequence=['#FC4C02']
)
fig_dias_por_mes.update_traces(textposition='outside')
fig_dias_por_mes.update_layout(
    title_x=0.5,
    xaxis_title="Mês",
    yaxis_title="Quantidade de Dias",
    plot_bgcolor='#C0C0C0'
)

# Gráfico 4: Análise de Pace vs. Distância
df_para_plotly = df.reset_index()
fig_pace_distancia = px.scatter(
    df_para_plotly,
    x='Distance',
    y='Average speed',
    color='Distance',
    size='Distance',
    hover_name='Activity Name',
    hover_data={'Activity date': '%d de %b, %Y'},
    labels={"Distance": "Distância da Corrida (km)", "Average speed": "Pace (minutos por km)"},
    title="Análise de Pace vs. Distância de Cada Corrida",
    color_continuous_scale='Rainbow'
)

# Construção do Dashboard

# Inicializar a aplicação Dash
app = dash.Dash(__name__)

# Definir o layout do dashboard
app.layout = html.Div(children=[
    html.H1(children='Dashboard das Análises de Corridas - Strava', style={'textAlign': 'center'}),

    html.Div(
        children=[
            # KPI 1: Total de Corridas
            html.Div(
                children=[
                    html.Div(f'{total_corridas}', style={'fontSize': 48, 'fontWeight': 'bold'}),
                    html.Div('Corridas Totais')
                ],
                style={'textAlign': 'center', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'width': '30%'}
            ),
            # KPI 2: Distância Total
            html.Div(
                children=[
                    html.Div(f'{total_distancia:.2f} km', style={'fontSize': 48, 'fontWeight': 'bold'}),
                    html.Div('Distância Total')
                ],
                style={'textAlign': 'center', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'width': '30%'}
            ),
            # KPI 3: Tempo Total
            html.Div(
                children=[
                    html.Div(tempo_formatado, style={'fontSize': 48, 'fontWeight': 'bold'}),
                    html.Div('Tempo Total de Corrida')
                ],
                style={'textAlign': 'center', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'width': '30%'}
            ),
        ],
        style={'display': 'flex', 'justifyContent': 'space-around', 'padding': '20px'}
    ),

    html.Hr(), # Adiciona uma linha horizontal para separar

    dcc.Graph(id='grafico-distancia-semana', figure=fig_distancia_semana),
    dcc.Graph(id='grafico-minutos-semana', figure=fig_minutos_semana),
    dcc.Graph(id='grafico-dias-mes', figure=fig_dias_por_mes),
    dcc.Graph(id='grafico-pace-distancia', figure=fig_pace_distancia)
])


# Abrir automático o navegador
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1, open_browser).start()
    app.run(debug=True)
    