import tkinter as tk
from gpiozero import AngularServo

servo = AngularServo(
    18,
    min_angle=-90,
    max_angle=90,
    min_pulse_width=0.001,
    max_pulse_width=0.002
)

def move_servo(value):
    angle = float(value)
    servo.angle = angle
    angle_label.config(text=f"Angle: {angle:.0f}°")

def close_program():
    servo.detach()
    servo.close()
    window.destroy()

window = tk.Tk()
window.title("Servo Controller")
window.geometry("450x180")

angle_label = tk.Label(window, text="Angle: 0°", font=("Arial", 18))
angle_label.pack(pady=20)

slider = tk.Scale(
    window,
    from_=-90,
    to=90,
    orient=tk.HORIZONTAL,
    length=400,
    resolution=1,
    command=move_servo
)
slider.set(0)
slider.pack()

window.protocol("WM_DELETE_WINDOW", close_program)
window.mainloop()
