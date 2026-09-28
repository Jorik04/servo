from signal import pause
from threading import Event, Lock, Thread
from time import sleep

import requests
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306


# Replace this with the Mac's IP address.
MAC_SERVER = "http://192.168.0.219:5050"

# Must match TOKEN in spotify_helper.py.
TOKEN = "lalimir"

HEADERS = {
    "X-Token": TOKEN
}


# --------------------------------------------------
# OLED
# --------------------------------------------------

oled_serial = i2c(port=1, address=0x3C)
oled = ssd1306(oled_serial, width=128, height=64)

display_lock = Lock()
stop_event = Event()


def shorten(text, length=20):
    if len(text) <= length:
        return text

    return text[:length - 3] + "..."


def format_time(seconds):
    seconds = max(0, int(seconds))
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"


def show_status(data):
    state = data.get("state", "stopped")
    title = data.get("title", "")
    artist = data.get("artist", "")
    position = data.get("position", 0)
    duration = data.get("duration", 0)

    symbol = ">" if state == "playing" else "||"

    with display_lock:
        with canvas(oled) as draw:
            if not title:
                draw.text(
                    (22, 25),
                    "Spotify stopped",
                    fill="white"
                )
                return

            draw.text(
                (0, 2),
                shorten(title),
                fill="white"
            )

            draw.text(
                (0, 20),
                shorten(artist),
                fill="white"
            )

            draw.text(
                (0, 42),
                f"{symbol} {format_time(position)} / "
                f"{format_time(duration)}",
                fill="white"
            )


def show_message(message):
    with display_lock:
        with canvas(oled) as draw:
            draw.text((0, 20), shorten(message), fill="white")


# --------------------------------------------------
# Spotify network requests
# --------------------------------------------------

def send_command(command):
    try:
        requests.post(
            f"{MAC_SERVER}/command/{command}",
            headers=HEADERS,
            timeout=2
        ).raise_for_status()

    except requests.RequestException as error:
        print(f"Command error: {error}")


def update_display_loop():
    while not stop_event.is_set():
        try:
            response = requests.get(
                f"{MAC_SERVER}/status",
                headers=HEADERS,
                timeout=2
            )

            response.raise_for_status()
            show_status(response.json())

        except requests.RequestException:
            show_message("Mac not connected")

        sleep(1)


# --------------------------------------------------
# Buttons
# --------------------------------------------------

factory = PiGPIOFactory(host="localhost")

previous_button = Button(
    17,
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.1
)

play_button = Button(
    27,
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.1
)

next_button = Button(
    22,
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.1
)

previous_button.when_pressed = lambda: send_command("previous")
play_button.when_pressed = lambda: send_command("playpause")
next_button.when_pressed = lambda: send_command("next")


# --------------------------------------------------
# Run
# --------------------------------------------------

show_message("Connecting...")

display_thread = Thread(
    target=update_display_loop,
    daemon=True
)

display_thread.start()

print("Spotify OLED controller started")
print("GPIO17: Previous")
print("GPIO27: Play/Pause")
print("GPIO22: Next")
print("Press Ctrl+C to stop")

try:
    pause()

except KeyboardInterrupt:
    print("\nStopped")

finally:
    stop_event.set()
    display_thread.join(timeout=2)

    oled.clear()

    previous_button.close()
    play_button.close()
    next_button.close()

    factory.close()