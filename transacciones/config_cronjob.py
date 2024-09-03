# config_cronjob.py

from crontab import CronTab
from mi_script import tarea_programada

def configurar_cronjob():
    # Configura el cronjob para ejecutar la función cada minuto
    cron = CronTab(user='nombre_de_usuario')  # Reemplaza 'nombre_de_usuario' con tu nombre de usuario
    job = cron.new(command="python -c 'from config_cronjob import tarea_programada; tarea_programada()'")
    job.setall('*/1 * * * *')  # Ejecutar cada minuto

    cron.write()

if __name__ == "__main__":
    configurar_cronjob()
