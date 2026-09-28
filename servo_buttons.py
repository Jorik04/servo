from signal import pause
from threading import Lock

from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306


# ==================================================
# OLED setup
# ==================================================

oled_serial = i2c(
    port=1,
    address=0x3C
)

oled = ssd1306(
    oled_serial,
    width=128,
    height=64
)

display_lock = Lock()


def display_angle(angle):
    """
    Display the requested target angle on the OLED.
    """

    # Convert -90...+90 into OLED position 2...125
    marker = int((angle + 90) / 180 * 123) + 2
    marker = max(2, min(125, marker))

    with display_lock:
        with canvas(oled) as draw:
            draw.text(
                (18, 5),
                "SERVO ANGLE",
                fill="white"
            )

            draw.text(
                (40, 27),
                f"{angle:+.0f} deg",
                fill="white"
            )

            # Angle indicator line
            draw.line(
                (2, 55, 125, 55),
                fill="white"
            )

            # Centre marker
            draw.line(
                (64, 51, 64, 59),
                fill="white"
            )

            # Current target marker
            draw.rectangle(
                (marker - 2, 52, marker + 2, 58),
                fill="white"
            )


# ==================================================
# Pigpio setup
# ==================================================

factory = PiGPIOFactory(
    host="localhost"
)


# ==================================================
# Servo setup
# ==================================================

# Servo signal:
# GPIO18, physical pin 12
servo = AngularServo(
    18,
    pin_factory=factory,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.001,
    max_pulse_width=0.002,
    initial_angle=0
)


# ==================================================
# Button setup
# ==================================================

# Left button:
# GPIO17, physical pin 11
left_button = Button(
    17,
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.05
)

# Right button:
# GPIO27, physical pin 13
right_button = Button(
    27,
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.05
)

# Centre button:
# GPIO22, physical pin 15
centre_button = Button(
    22,
    pin_factory=factory,
    pull_up=True,
    bounce_time=0.05
)


# ==================================================
# Button actions
# ==================================================

target_angle = 0


def move_to(angle):
    """
    Send one target position to the servo.

    The servo's internal controller performs the
    movement smoothly at its natural speed.
    """

    global target_angle

    target_angle = angle
    servo.angle = angle

    print(f"Moving to {angle:+.0f} degrees")
    display_angle(angle)


def move_left():
    move_to(-90)


def move_right():
    move_to(90)


def move_centre():
    move_to(0)


left_button.when_pressed = move_left
right_button.when_pressed = move_right
centre_button.when_pressed = move_centre


# ==================================================
# Start controller
# ==================================================

display_angle(0)

print("Servo controller started")
print("LEFT   GPIO17: move to -90 degrees")
print("RIGHT  GPIO27: move to +90 degrees")
print("CENTRE GPIO22: move to 0 degrees")
print("Press Ctrl+C to stop")


# ==================================================
# Keep program running
# ==================================================

try:
    pause()

except KeyboardInterrupt:
    print("\nController stopped")

finally:
    servo.detach()
    oled.clear()

    servo.close()
    left_button.close()
    right_button.close()
    centre_button.close()

    factory.close()