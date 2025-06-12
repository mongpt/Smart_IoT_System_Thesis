import socket
import struct
import pyRTOS
from rpi_hardware_pwm import HardwarePWM
from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time
from time import sleep

# Client configuration
SERVER_IP = '192.168.2.50'
SERVER_PORT = 12345

# Create a TCP socket
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket = None

# Setup the PWM
freq = 15000
# Define PWM for GPIO 12
L_motor = HardwarePWM(pwm_channel=0, hz=freq, chip=2)  #GPIO 12 for pwm
# Define PWM for GPIO 13
R_motor = HardwarePWM(pwm_channel=1, hz=freq, chip=2)  # GPIO 13

left_y = 0
current_duty = 0

# Setup DIR pins
L_dir = DigitalOutputDevice(20, active_high=True)
R_dir = DigitalOutputDevice(21, active_high=False)

# Constants for speed measurement
PULSES_PER_REV = 21  # Number of pulses per revolution
last_pulse = 0
pulse_period = 0
pulse_count = 0

turn_left = False
turn_right = False

def connect_to_server():
    global client_socket
    """Attempts to connect to the server with retries."""
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Attempting to connect to server at {SERVER_IP}:{SERVER_PORT}...")
            client_socket.connect((SERVER_IP, SERVER_PORT))
            print(f"Successfully connected to server at {SERVER_IP}:{SERVER_PORT}")
            return
        except ConnectionRefusedError:
            print("Server not available. Retrying in 2 seconds...")
            client_socket.close()
            sleep(2)

# Callback function to count pulses
def fg_callback():
    global last_pulse, pulse_period, pulse_count
    now = time.time() * 1000000  # Get current time in microseconds
    if last_pulse != 0:
        pulse_period += now - last_pulse  # Add time since last pulse
        pulse_count += 1  # Increment pulse count
    last_pulse = now  # Update last pulse time

def calculate_speed_task(self):
    global pulse_period, pulse_count
    fg_pin = DigitalInputDevice(16, pull_up=True)
    fg_pin.when_activated = fg_callback  # Attach the pulse_detected function to the FG pin
    yield

    while True:
        try:
            if pulse_count > 0:
                # Calculate average period per pulse
                period_per_pulse = pulse_period / pulse_count

                # Calculate RPM: (60 seconds * 1,000,000 us per minute) / (Pulses per revolution * period in us)
                speed = (60.0 * 1000000) / (PULSES_PER_REV * period_per_pulse)
                
                # Reset counters for the next measurement cycle
                pulse_count = 0
                pulse_period = 0
            else:
                speed = 0
            
            print(f"Motor Speed: {speed:.2f} RPM")

            # Send the speed data to the server
            speed_message = struct.pack('f', speed)  # Pack speed into binary format
            client_socket.sendall(speed_message)
            #speed_message = str(speed)
            #client_socket.sendall(speed_message.encode())
        except (socket.error, BrokenPipeError):
            print("Server not available. Retrying...")
            connect_to_server()

        yield [pyRTOS.timeout(0.1)]

def receive_joystick_task(self):
    global left_y, turn_left, turn_right
    while True:
        try:
            data = client_socket.recv(12)  # Receive up to 1024 bytes
            if data:
                left_y, turn_left, turn_right = struct.unpack('fii', data)  # Unpack joystick values
                #print(f"Received values - Left Y: {left_y}, Turn Left: {turn_left}, Turn Right: {turn_right}")
                #print(data)
        except (socket.error, BrokenPipeError):
            print("Server not available. Retrying...")
            connect_to_server()
            
        yield [pyRTOS.timeout(0.001)]

def pwm_task(self):
    global current_duty
    global left_y
    global turn_left
    global turn_right

    was_left = was_right = False

    L_motor.start(current_duty)  # Start PWM with initial duty cycle
    R_motor.start(current_duty)

    yield

    while True:
        if left_y < 0:
            L_dir.on()
            R_dir.on()
        elif left_y > 0:
            L_dir.off()
            R_dir.off()

        new_duty = abs(int(left_y * 100))
        if new_duty != current_duty:
            # Gradually adjust to the new duty cycle
            step = 1 if new_duty > current_duty else -1
            for d in range(current_duty, new_duty, step):
                if turn_left:
                    d_left = int(d/2)
                    d_right = d
                    was_left = True
                elif turn_right:
                    d_left = d
                    d_right = int(d/2)
                    was_right = True
                else:
                    d_left = d_right = d
                    was_left = was_right = False
                # Change the PWM duty cycle
                L_motor.change_duty_cycle(d_left)
                R_motor.change_duty_cycle(d_right)
                # Keep your original delay loop for smooth transitions
                for i in range(1000):
                    for j in range(100):
                        pass

            current_duty = new_duty  # update current duty

        if turn_left or turn_right:
            if turn_left:
                d_left = int(current_duty/2)
                d_right = current_duty
                was_left = True
            elif turn_right:
                d_left = current_duty
                d_right = int(current_duty/2)
                was_right = True
            # Change the PWM duty cycle
            L_motor.change_duty_cycle(d_left)
            R_motor.change_duty_cycle(d_right)

        else:
            if was_left:
                for d in range(d_left, d_right, 1):
                    L_motor.change_duty_cycle(d)
                    for i in range(1000):
                        for j in range(100):
                            pass
                d_left = d_right
                was_left = False

            if was_right:
                for d in range(d_right, d_left, 1):
                    R_motor.change_duty_cycle(d)
                    for i in range(1000):
                        for j in range(100):
                            pass
                d_right = d_left
                was_right = False
                
        yield [pyRTOS.timeout(0.01)]  # Task yielding


# Main execution
if __name__ == "__main__":
    try:
        connect_to_server()
        pyRTOS.add_task(pyRTOS.Task(pwm_task, name="pwm_task"))
        pyRTOS.add_task(pyRTOS.Task(calculate_speed_task, name="speed_task"))  # Add speed task
        pyRTOS.add_task(pyRTOS.Task(receive_joystick_task, name="receive_joystick_task"))  # Add joystick receive task
        pyRTOS.start()
    except KeyboardInterrupt:
        for d in range(current_duty, 0, -1):
            L_motor.change_duty_cycle(d)
            R_motor.change_duty_cycle(d)
            sleep(0.01)
        L_motor.stop()
        R_motor.stop()
        if client_socket:
            client_socket.close()  # Close socket connection

