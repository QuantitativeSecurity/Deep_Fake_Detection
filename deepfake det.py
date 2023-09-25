import socket
import cv2
import numpy as np
import deepfake_detection_toolkit as fd

# Define IP addresses to broadcast to
ip_addresses = ['X.X.X.X', 'X.X.X.X']

# Create a socket for each IP address
sockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in ip_addresses]

# Connect the sockets to the IP addresses
for i, s in enumerate(sockets):
    try:
        s.connect((ip_addresses[i], 12345))
    except socket.error as e:
        print(f'Failed to connect to {ip_addresses[i]}: {e}')
        s.close()
        sockets[i] = None

# Remove any invalid sockets
sockets = [s for s in sockets if s is not None]

if not sockets:
    print('Failed to connect to any IP addresses')
    exit()

# Capture the camera feed using OpenCV
cap = cv2.VideoCapture(0)

# Load the deepfake detection model
model = fd.load_model()

# Continuously read and broadcast frames
while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame is a deepfake
    is_deepfake = fd.detect(model, frame)

    # Only broadcast the frame if it's not a deepfake
    if not is_deepfake:
        # Encode the frame as a JPEG
        _, jpeg = cv2.imencode('.jpg', frame)

        # Convert the encoded frame to bytes
        frame_bytes = jpeg.tobytes()

        # Broadcast the frame to each socket
        for s in sockets:
            try:
                s.sendall(frame_bytes)
            except socket.error as e:
                print(f'Failed to send frame to {s.getpeername()}: {e}')
                s.close()
                sockets.remove(s)

        # Check if there are any sockets left
        if not sockets:
            print('Lost connection to all IP addresses')
            break

# Clean up
