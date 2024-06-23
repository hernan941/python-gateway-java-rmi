from datetime import datetime

def format_log(ini_or_fin, game ,type_operation, team = "", user = "", play = None):
    timestamp = datetime.now().timestamp()
    if team != "" and user != "" and play != "":
        return f"{timestamp},{ini_or_fin},juego{game},{type_operation},equipo{team},jugador{user},{play}"
    elif team and user:
        return f"{timestamp},{ini_or_fin},juego{game},{type_operation},equipo{team},jugador{user}"
    elif team:
        return f"{timestamp},{ini_or_fin},juego{game},{type_operation},equipo{team}"
    else:
        return f"{timestamp},{ini_or_fin},juego{game},{type_operation}"