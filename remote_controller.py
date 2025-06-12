import struct
import pygame
import socket
import threading
import time
from math import pi

# Server configuration
SERVER_IP = '192.168.2.197'
SERVER_PORT = 12345

# Define constants for joystick button mappings and server configuration
TURN_LEFT_BTN = 1
TURN_RIGHT_BTN = 2

speed = 0

GEAR_RATIO = 108
WHEEL_DIAMETER = 0.13

def send_joystick_data(connection, stop_event):
    """Send joystick data to the client."""
    try:
        # Initialize pygame
        pygame.init()
        pygame.joystick.init()

        # Connect to the first joystick
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Connected to {joystick.get_name()}")

        while not stop_event.is_set():
            pygame.event.pump()  # Update internal event queue
            left_y = joystick.get_axis(1)
            turn_left = joystick.get_button(TURN_LEFT_BTN)
            turn_right = joystick.get_button(TURN_RIGHT_BTN)

            # Pack and send data
            packed_data = struct.pack('fii', left_y, turn_left, turn_right)
            connection.sendall(packed_data)
            #print(packed_data)
            time.sleep(0.01)

    except Exception as e:
        print(f"Error sending data: {e}")
    finally:
        print("Stopping joystick data thread.")
        stop_event.set()


def handle_client(connection, client_address):
    global speed
    """Handle communication with a single client."""
    print(f"Connected to client: {client_address}")

    # Use a threading event to manage thread termination
    stop_event = threading.Event()

    # Start sending joystick data in a separate thread
    send_thread = threading.Thread(target=send_joystick_data, args=(connection, stop_event), daemon=True)
    send_thread.start()

    try:
        while True:
            data = connection.recv(4)
            if not data:
                print("Client disconnected.")
                break

            # Unpack and print the received data
            motor_rpm = struct.unpack('f', data)[0]
            wheel_rpm = float(motor_rpm) / GEAR_RATIO
            speed = wheel_rpm * (pi * WHEEL_DIAMETER) / 60  # velocity = m/s
            print(f"Robot speed: {speed:.2f} m/s")

    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        # Signal the send thread to stop
        stop_event.set()
        send_thread.join()
        connection.close()
        print(f"Connection with client {client_address} closed.")


def start_server():
    """Start the server and accept multiple clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    try:
        while True:
            connection, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(connection, client_address), daemon=True).start()

    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    start_server()
