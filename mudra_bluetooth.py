#!/usr/bin/env python3
"""
Mudra Bluetooth Interface - Connect to Mudra band
"""

import bluetooth
import json
import threading
from mudra_complete import MudraComplete

class MudraBluetoothInterface:
    def __init__(self):
        self.system = MudraComplete()
        self.socket = None
        self.connected = False
        
    def scan_for_mudra(self):
        """Scan for Mudra band device"""
        print("Scanning for Mudra band...")
        devices = bluetooth.discover_devices(lookup_names=True)
        
        for addr, name in devices:
            if "mudra" in name.lower() or "wearable" in name.lower():
                print(f"Found potential Mudra device: {name} ({addr})")
                return addr
        
        print("No Mudra device found")
        return None
    
    def connect_to_mudra(self, address=None):
        """Connect to Mudra band"""
        if not address:
            address = self.scan_for_mudra()
            if not address:
                return False
        
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((address, 1))  # RFCOMM channel 1
            self.connected = True
            print(f"Connected to Mudra band at {address}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def listen_for_gestures(self):
        """Listen for gesture data from Mudra band"""
        if not self.connected:
            return
            
        print("Listening for gestures...")
        
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if data:
                    self.process_gesture_data(data)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    
    def process_gesture_data(self, data):
        """Process incoming gesture data"""
        try:
            # Assuming Mudra sends JSON format like:
            # {"gesture": "tap", "position": [x, y]} or {"gesture": "twist"}
            gesture_data = json.loads(data)
            gesture_type = gesture_data.get("gesture")
            
            if gesture_type == "tap":
                position = gesture_data.get("position")
                if position:
                    self.system.handle_gesture("tap", tuple(position))
                else:
                    self.system.handle_gesture("tap")
                    
            elif gesture_type == "reverse_tap":
                self.system.handle_gesture("reverse_tap")
                
            elif gesture_type == "twist":
                self.system.handle_gesture("twist")
                
            elif gesture_type == "double_twist":
                self.system.handle_gesture("double_twist")
                
            elif gesture_type == "pinch_start":
                modifier = gesture_data.get("modifier", "shift")
                self.system.handle_gesture("pinch_hold_start", modifier)
                
            elif gesture_type == "pinch_end":
                modifier = gesture_data.get("modifier", "shift")
                self.system.handle_gesture("pinch_hold_end", modifier)
                
            elif gesture_type == "slide":
                direction = gesture_data.get("direction")
                self.system.handle_gesture("reverse_pinch_slide", direction)
                
            elif gesture_type == "hand_position":
                position = gesture_data.get("position")
                if position:
                    self.system.handle_gesture("hand_position", tuple(position))
                    
        except json.JSONDecodeError:
            # Handle raw gesture strings if not JSON
            data = data.strip()
            if data in ["tap", "reverse_tap", "twist", "double_twist"]:
                self.system.handle_gesture(data)
    
    def start(self, address=None):
        """Start the Bluetooth interface"""
        if self.connect_to_mudra(address):
            listener_thread = threading.Thread(target=self.listen_for_gestures)
            listener_thread.daemon = True
            listener_thread.start()
            return True
        return False
    
    def stop(self):
        """Stop the interface"""
        self.connected = False
        if self.socket:
            self.socket.close()
        print("Mudra Bluetooth interface stopped")

if __name__ == "__main__":
    interface = MudraBluetoothInterface()
    
    print("🎯 Mudra Bluetooth Interface")
    print("Make sure your Mudra band is paired and discoverable")
    
    if interface.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            interface.stop()
    else:
        print("Failed to connect to Mudra band")