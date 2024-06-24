#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import warnings
warnings.filterwarnings("ignore")


# In[ ]:


# load libraries
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns


# In[ ]:


from dotenv import load_dotenv
load_dotenv()
time_window_seconds = int(os.getenv('TIME_WINDOW_SECONDS', 100))


# In[ ]:


file_path = "../log/log.txt"

def read_log_file(file_path):
    rows = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 4:
                rows.append(parts + [None, None, None])
            elif len(parts) == 6:
                rows.append(parts + [None])
            elif len(parts) == 7:
                rows.append(parts)
    return pd.DataFrame(rows, columns = ['timestamp', 'action', 'game', 'event', 'team', 'player', 'move'])

df_log = read_log_file(file_path)

df_log["timestamp"] = pd.to_datetime(pd.to_numeric(df_log["timestamp"], errors='coerce'), unit='s')


# In[ ]:


df_log


# In[ ]:


# Data para Gráfico 1: Jugadores creador por equipo en un juego.
data_plot1 = df_log[(df_log["action"] == "fin") & 
                    (df_log["event"] == "crea-jugador")]

# Contar la cantidad de jugadores por partida
#df1 = pd.read_excel("ejemplos/ejemplo1.xlsx") # df de ejemplo, usar para verificar congruencia de informacion
df1 = data_plot1.groupby(['game', 'team']).size().reset_index(name='count')
df1


# In[ ]:





# In[ ]:


sns.set(style="whitegrid")

plt.figure(figsize=(10, 6))
sns.barplot(x='game', y='count', hue='team', data=df1, palette='viridis')

plt.title('Cantidad de Jugadores por Partida y por Equipo')
plt.xlabel('Partida')
plt.ylabel('Cantidad de Jugadores')

output_folder = 'resultados'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_path = os.path.join(output_folder, '[1] Cantidad de Jugadores.png')
plt.savefig(output_path)
print(f'Gráfico guardado en: {output_path}')

plt.show()


# In[ ]:


data_plot2 = df_log[(df_log["event"] == 'lanza-dado') & 
                    (df_log["action"] == 'fin')]

#df2 = pd.read_excel("ejemplos/ejemplo2.xlsx") # ejemplo para verificar congruencia de los datos y el grafico
df2 = data_plot2.groupby(['game', 'player']).size().reset_index(name='count')


# In[ ]:


plt.figure(figsize=(10, 6))
sns.barplot(x='game', y='count', hue='player', data=df2, palette='viridis')

plt.title('Cantidad de Jugadas por equipo y por jugador')
plt.xlabel('Partida')
plt.ylabel('Cantidad de Jugadas')

output_folder = 'resultados'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_path = os.path.join(output_folder, '[2] Cantidad de Jugadas.png')
plt.savefig(output_path)
print(f'Gráfico guardado en: {output_path}')

plt.show()


# In[ ]:


#data_plot3 = pd.read_excel("ejemplos/ejemplo3.xlsx") # usar en caso de test etc
data_plot3 = df_log[(df_log["action"] == 'fin') & 
                    (df_log["event"] == 'lanza-dado')]

start_time = data_plot3["timestamp"].min()
end_time = start_time + pd.Timedelta(seconds=time_window_seconds)
data_plot3 = data_plot3[(data_plot3["timestamp"] >= start_time) & 
                        (data_plot3["timestamp"] <= end_time)]

data_plot3 = data_plot3.sort_values(by = ['game', 'team', "timestamp"])
data_plot3["move"] = pd.to_numeric(data_plot3['move'])
data_plot3['cumulative_score'] = data_plot3.groupby(['game', 'team'])['move'].cumsum()
data_plot3[["timestamp", "game", "team", "cumulative_score"]]


# In[ ]:


def plot_cumulative_score(df, game_name, output_folder):
    df_game = df[df['game'] == game_name]

    df_game['timestamp'] = pd.to_datetime(df_game['timestamp'])

    teams = df_game['team'].unique()
    
    plt.figure(figsize=(14, 7))
    
    for team in teams:
        df_team = df_game[df_game['team'] == team]
        sns.lineplot(x='timestamp', y='cumulative_score', data=df_team, marker='o', label=f'{game_name} - {team}')
    
    plt.xlabel('Tiempo')
    plt.ylabel('Puntaje acumulado')
    plt.title(f'Curvas de puntuación de {game_name}')
    plt.legend()
    plt.grid(True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, f'[3] {game_name}.png')
    plt.savefig(output_path)
    plt.close()
    print(f'grafico guardado en: {output_path}')
    
for juego in data_plot3["game"].unique():
    plot_cumulative_score(data_plot3, juego, 'resultados')


# In[ ]:


data_plot4 = df_log[(df_log["action"] == 'fin') & 
                    (df_log["event"] == 'crea-jugador')]

start_time = data_plot4["timestamp"].min()
end_time = start_time + pd.Timedelta(seconds=time_window_seconds)
data_plot4 = data_plot4[(data_plot4["timestamp"] >= start_time) & 
                        (data_plot4["timestamp"] <= end_time)].sort_values(by = "timestamp").drop_duplicates(subset = ['game', 'team'], keep = 'first')

data_plot4['teams_created'] = data_plot4.groupby('game').cumcount() + 1
data_plot4


# In[ ]:


def plot_teams_created(df, game_name, output_folder):
    df_game = df[df['game'] == game_name]

    df_game['timestamp'] = pd.to_datetime(df_game['timestamp'])

    df_game = df_game.sort_values(by='timestamp')

    df_game['teams_created'] = df_game.groupby('game').cumcount() + 1

    plt.figure(figsize=(14, 7))
    sns.lineplot(x='timestamp', y='teams_created', data=df_game, marker='o')
    
    plt.xlabel('Tiempo')
    plt.ylabel('Cantidad de equipos creados')
    plt.title(f'Cantidad de equipos creados en el tiempo para {game_name}')
    plt.grid(True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, f'[4] {game_name}.png')
    plt.savefig(output_path)
    plt.close()
    print(f'grafico guardado en: {output_path}')
    
for juego in data_plot4["game"].unique():
    plot_teams_created(data_plot4, juego, 'resultados')


# In[ ]:


data_plot5 = df_log[(df_log["action"] == 'fin') & 
                    (df_log["event"] == 'crea-jugador')]#

start_time = data_plot5["timestamp"].min()
end_time = start_time + pd.Timedelta(seconds=time_window_seconds)
data_plot5 = data_plot5[(data_plot5["timestamp"] >= start_time) & 
                        (data_plot5["timestamp"] <= end_time)].sort_values(by = ["game", "timestamp"])

data_plot5['players_created'] = data_plot5.groupby('game').cumcount() + 1
data_plot5


# In[ ]:


def plot_players_created(df, game_name, output_folder):
    df_game = df[df['game'] == game_name]

    df_game['timestamp'] = pd.to_datetime(df_game['timestamp'])

    df_game = df_game.sort_values(by='timestamp')

    df_game['players_created'] = df_game.groupby('game').cumcount() + 1

    plt.figure(figsize=(14, 7))
    sns.lineplot(x='timestamp', y='players_created', data=df_game, marker='o')
    
    plt.xlabel('Tiempo')
    plt.ylabel('Cantidad de jugadores creados')
    plt.title(f'Cantidad de jugadores creados en el tiempo para {game_name}')
    plt.grid(True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, f'[5] {game_name}.png')
    plt.savefig(output_path)
    plt.close()
    print(f'grafico guardado en: {output_path}')
    
for juego in data_plot5["game"].unique():
    plot_players_created(data_plot5, juego, 'resultados')


# In[ ]:




