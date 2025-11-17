import requests
import datetime
import sys
import tkinter as tk
from dateutil import parser

# --- НАСТРОЙКИ ---
API_URL = "https://start.vag.de/dm/api/v1/abfahrten.json/vgn/1431?timedelay=0&product=Ubahn,Bus,Tram,SBahn,RBahn"
UPDATE_INTERVAL = 1000


root = tk.Tk()
root.title("Табло: Mögeldorf (ID: 1431)")
root.geometry("400x450")


schedule_text = tk.StringVar()
schedule_text.set("Загружаю данные...")


schedule_label = tk.Label(
    root,
    textvariable=schedule_text,
    font=("Consolas", 12),
    justify=tk.LEFT,
    padx=10,
    pady=10
)
schedule_label.pack(anchor="nw")


def fetch_and_update_schedule():
    print(f"\nОбновляю... {datetime.datetime.now().strftime('%H:%M:%S')}")

    try:
        response = requests.get(API_URL)
        response.raise_for_status()

        response_data = response.json()

        if 'Abfahrten' not in response_data:
            schedule_text.set("Ошибка: API не вернул 'Abfahrten'.")
            return

        departures = response_data['Abfahrten']

        if not departures:
            schedule_text.set("На ближайшее время отправлений нет.")
            return


        first_departure_time = parser.parse(departures[0]['AbfahrtszeitIst'])
        now = datetime.datetime.now(first_departure_time.tzinfo)

        display_string = f"--- Mögeldorf --- \n(Обновлено: {now.strftime('%H:%M:%S')})\n\n"

        for dep in departures:
            line = dep['Linienname']
            direction = dep['Richtungstext']
            when_time = parser.parse(dep['AbfahrtszeitIst'])

            delta = when_time - now
            minutes_left = int(delta.total_seconds() / 60)

            if minutes_left <= 0:
                display_string += f"  {line:>5} -> {direction} - СЕЙЧАС\n"
            else:
                display_string += f"  {line:>5} -> {direction} - {minutes_left} мин\n"


        schedule_text.set(display_string)

    except requests.exceptions.HTTPError as e:
        schedule_text.set(f"Ошибка HTTP: {e}\n(VAG API 'лежит'?)")
    except requests.exceptions.RequestException as e:
        schedule_text.set(f"Ошибка сети:\n{e}\n(Проверь интернет)")
    except Exception as e:
        schedule_text.set(f"Неизвестная ошибка:\n{e}")

    finally:

        root.after(UPDATE_INTERVAL, fetch_and_update_schedule)



fetch_and_update_schedule()

root.mainloop()