# iiprint_real.py - FULLSCREEN RESPONSIVE VERSION (FIXED FOR SMALL SCREENS)

import tkinter as tk
from tkinter import messagebox, ttk
import serial
import time
import threading
import json
import os
import hashlib
import subprocess

class STIMOFingerprintAuth:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("STIMO Security - Real Fingerprint")
        
        # FULLSCREEN SETUP
        self.root.attributes('-fullscreen', True)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Dynamic sizing based on screen resolution - OPTIMIZED FOR SMALL SCREENS
        self.title_font_size = max(20, int(min(self.screen_width, self.screen_height) * 0.03))
        self.normal_font_size = max(12, int(min(self.screen_width, self.screen_height) * 0.025))
        self.small_font_size = max(10, int(min(self.screen_width, self.screen_height) * 0.02))
        self.large_icon_size = max(40, int(self.screen_height * 0.08))
        self.normal_icon_size = max(30, int(self.screen_height * 0.06))
        self.button_width = max(12, int(self.screen_width * 0.008))
        self.button_height = max(1, int(self.screen_height * 0.002))
        
        print(f"Screen: {self.screen_width}x{self.screen_height}")
        print(f"Font Sizes - Title: {self.title_font_size}, Normal: {self.normal_font_size}, Small: {self.small_font_size}")
        
        self.root.configure(bg='#0A0E29')
        
        # AS608 Configuration for Raspberry Pi GPIO
        self.fingerprint_port = "/dev/ttyS0"  # GPIO serial
        self.baudrate = 57600
        self.ser = None
        self.fingerprint_connected = False
        
        # Security files
        self.users_file = "stimo_users.json"
        self.setup_security()
        
        self.current_screen = "fingerprint"
        self.scanning = False
        self.enrolling = False
        self.current_focused_entry = None
        self.login_processed = False
        self.enrollment_step = 0
        self.current_enrollment_id = None
        self.template_buffer = bytearray()
        
        # Initialize AS608 with retry mechanism
        self.initialize_as608_with_retry()
        self.show_fingerprint_screen()
        
        # Start fingerprint scanning
        self.start_fingerprint_scanning()
        
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # 🔹 Preload STIMO launcher in background (hidden, waiting for trigger)
        import subprocess
        self.stimo_process = subprocess.Popen(
            ["python3", "main.py"],
            cwd="/home/stimo/STIMO_Mode"
        )
        print("✅ Preloading STIMO main.py in background...")



    def initialize_as608_with_retry(self):
        """Initialize AS608 with multiple retry attempts"""
        max_retries = 5
        for attempt in range(max_retries):
            print(f"🔄 AS608 Initialization Attempt {attempt + 1}/{max_retries}")
            if self.initialize_as608():
                self.fingerprint_connected = True
                print("✅ AS608 Initialization Successful!")
                return True
            time.sleep(2)
        
        # Try alternative ports
        alternative_ports = ["/dev/ttyAMA0", "/dev/serial0"]
        for port in alternative_ports:
            print(f"🔄 Trying alternative port: {port}")
            self.fingerprint_port = port
            if self.initialize_as608():
                self.fingerprint_connected = True
                print(f"✅ AS608 Connected on {port}!")
                return True
            time.sleep(1)
        
        print("❌ AS608 Initialization Failed after all attempts")
        self.fingerprint_connected = False
        return False

    def initialize_as608(self):
        """Initialize AS608 Fingerprint Reader with improved timing"""
        try:
            print(f"🔄 Initializing AS608 on {self.fingerprint_port} at {self.baudrate} baud...")
            
            # Close existing connection
            if self.ser and self.ser.is_open:
                self.ser.close()
                time.sleep(1)
            
            # Create serial connection with longer timeout
            self.ser = serial.Serial(
                port=self.fingerprint_port,
                baudrate=self.baudrate,
                timeout=5,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Extended initialization delay for sensor warm-up
            print("⏳ Warming up sensor...")
            time.sleep(4)
            
            # Clear all buffers
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            time.sleep(1)
            
            # Test communication with extended retry
            for attempt in range(5):
                print(f"🔄 Sensor check attempt {attempt + 1}/5")
                if self.check_sensor():
                    print("✅ AS608 Sensor Check PASSED!")
                    return True
                print(f"⚠️ Sensor check {attempt + 1} failed, retrying...")
                time.sleep(1.5)
            
            print("❌ AS608 Sensor Check FAILED after 5 attempts")
            if self.ser:
                self.ser.close()
            self.ser = None
            return False
            
        except Exception as e:
            print(f"❌ AS608 Connection Error: {e}")
            self.ser = None
            return False

    def check_sensor(self):
        """Improved sensor check with better response handling"""
        try:
            # AS608 Get Template Count command
            cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x1D, 0x00, 0x21])
            
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            time.sleep(1.0)
            
            response = self.ser.read(16)
            
            if response and len(response) >= 12:
                if response[0] == 0xEF and response[1] == 0x01:
                    confirmation_code = response[9]
                    if confirmation_code == 0x00:
                        template_count = response[11]
                        print(f"✅ AS608 Responding! Template count: {template_count}")
                        return True
                    else:
                        print(f"⚠️ AS608 Response with error code: {confirmation_code:02x}")
                else:
                    print(f"❌ Invalid packet header: {response.hex()}")
            else:
                print(f"❌ No valid response from sensor")
                
            return False
            
        except Exception as e:
            print(f"❌ Check Sensor Error: {e}")
            return False

    def wait_for_fingerprint(self, timeout=30):
        """Improved finger detection with better timing"""
        print(f"⏳ Waiting for finger on sensor (timeout: {timeout}s)...")
        
        start_time = time.time()
        last_status_time = start_time
        
        while time.time() - start_time < timeout:
            try:
                # Command to check if finger is present - PS_GetImage
                cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05])
                self.ser.reset_input_buffer()
                self.ser.write(cmd)
                time.sleep(0.8)  # Increased delay for better detection
                
                response = self.ser.read(12)
                
                if response and len(response) >= 12:
                    confirmation_code = response[9]
                    
                    if confirmation_code == 0x00:  # ✅ Finger detected!
                        print("✅ Finger detected on sensor!")
                        return True
                    elif confirmation_code == 0x01:  # No finger
                        # Only print status every 5 seconds to avoid spam
                        if time.time() - last_status_time >= 3:
                            print("⏳ Waiting for finger...")
                            last_status_time = time.time()
                    elif confirmation_code == 0x02:  # Can't detect finger
                        print("⚠️ Sensor can't detect finger clearly")
                    else:
                        print(f"⚠️ Sensor response code: {confirmation_code:02x}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Error in fingerprint detection: {e}")
                return False
        
        print("❌ No finger detected within timeout period")
        return False

    def capture_fingerprint_image(self):
        """Capture fingerprint image with better timing"""
        try:
            print("📸 Capturing fingerprint image...")
            
            # Command to generate image - PS_GenImg
            cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05])
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            time.sleep(2.5)  # Increased capture time for better image
            
            response = self.ser.read(12)
            
            if response and len(response) >= 12:
                confirmation_code = response[9]
                
                if confirmation_code == 0x00:  # Successful image capture
                    print("✅ Fingerprint image captured successfully!")
                    return True
                elif confirmation_code == 0x01:
                    print("❌ Error receiving data package")
                elif confirmation_code == 0x02:
                    print("❌ No finger detected during capture")
                elif confirmation_code == 0x03:
                    print("❌ Failed to generate fingerprint image")
                else:
                    print(f"❌ Image capture failed with code: {confirmation_code:02x}")
                
                return False
            else:
                print("❌ No response from sensor during image capture")
                return False
                
        except Exception as e:
            print(f"❌ Error in image capture: {e}")
            return False

    def generate_character_file(self, buffer_number):
        """Generate character file from captured image with improved timing"""
        try:
            print(f"🔄 Generating character file in buffer {buffer_number}...")
            
            # PS_GenChar command
            cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, buffer_number, 0x00])
            # Calculate checksum
            data = cmd[6:]
            checksum = (sum(data) & 0xFF)
            cmd = cmd + bytes([checksum])
            
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            time.sleep(2.0)  # Increased processing time
            
            response = self.ser.read(12)
            if response and len(response) >= 12:
                confirmation_code = response[9]
                
                if confirmation_code == 0x00:
                    print(f"✅ Character file generated in buffer {buffer_number}")
                    return True
                elif confirmation_code == 0x06:
                    print("❌ Invalid character file (messy image)")
                elif confirmation_code == 0x07:
                    print("❌ Too few fingerprint features")
                else:
                    print(f"❌ Character generation failed: {confirmation_code:02x}")
                    
            return False
        except Exception as e:
            print(f"❌ Error generating character file: {e}")
            return False

    def create_template(self):
        """Create template from character files with improved timing"""
        try:
            print("🔄 Creating fingerprint template...")
            
            # PS_RegModel command
            cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x05, 0x00, 0x09])
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            time.sleep(2.5)  # Extended wait for template creation
            
            response = self.ser.read(12)
            if response and len(response) >= 12:
                confirmation_code = response[9]
                
                if confirmation_code == 0x00:
                    print("✅ Template created successfully!")
                    return True
                elif confirmation_code == 0x0A:
                    print("❌ Error: Two fingerprints don't match")
                elif confirmation_code == 0x0B:
                    print("❌ Error: Failed to combine character files")
                else:
                    print(f"❌ Template creation failed: {confirmation_code:02x}")
                    
            return False
        except Exception as e:
            print(f"❌ Error creating template: {e}")
            return False

    def store_template(self, template_id):
        """Store template in specified location with improved error handling"""
        try:
            page_id_low = template_id & 0xFF
            
            print(f"💾 Storing template at ID: {template_id}...")
            
            # PS_StoreChar command
            cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x06, 0x06, 0x01, 0x00, page_id_low, 0x00])
            # Calculate checksum
            data = cmd[6:]
            checksum = (sum(data) & 0xFF)
            cmd = cmd + bytes([checksum])
            
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            time.sleep(1.5)
            
            response = self.ser.read(12)
            if response and len(response) >= 12:
                confirmation_code = response[9]
                
                if confirmation_code == 0x00:
                    print(f"✅ Template stored successfully! ID: {template_id}")
                    return True
                elif confirmation_code == 0x0B:
                    print("❌ Error: Invalid template position")
                elif confirmation_code == 0x18:
                    print("❌ Error: Flash writing error")
                else:
                    print(f"❌ Template storage failed: {confirmation_code:02x}")
                    
            return False
        except Exception as e:
            print(f"❌ Error storing template: {e}")
            return False

    def search_fingerprint(self):
        """🆕 WORKING SEARCH METHOD FROM SECOND CODE"""
        try:
            # AS608 SEARCH COMMAND - Working method from second code
            cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x08, 0x04, 0x01, 0x00, 0x00, 0x00, 0xA3, 0x00])
            # Calculate checksum
            data = cmd[6:]
            checksum = (sum(data) & 0xFF)
            cmd = cmd + bytes([checksum])
            
            self.ser.reset_input_buffer()
            self.ser.write(cmd)
            time.sleep(2.5)  # Longer wait for reliable search
            response = self.ser.read(16)
            
            if response and len(response) >= 16 and response[9] == 0x00:
                fingerprint_id = response[10] * 256 + response[11]
                match_score = response[12] * 256 + response[13]
                
                print(f"🎯 FINGERPRINT FOUND! ID: {fingerprint_id}, Score: {match_score}")
                return True, fingerprint_id, match_score
            else:
                print(f"❌ No match found")
                return False, 0, 0
                
        except Exception as e:
            print(f"❌ Fingerprint search error: {e}")
            return False, 0, 0

    def capture_fingerprint_with_retry(self, max_retries=5):
        """Capture fingerprint with extended retry mechanism"""
        for attempt in range(max_retries):
            print(f"🔄 Capture attempt {attempt + 1}/{max_retries}")
            
            if self.capture_fingerprint_image():
                return True
                
            if attempt < max_retries - 1:
                print(f"🔄 Retrying capture in 2 seconds...")
                time.sleep(2)
                
        return False

    def enroll_fingerprint(self):
        """IMPROVED: Real fingerprint enrollment with VERIFICATION STEP"""
        try:
            # Check sensor connection first
            if not self.fingerprint_connected or not self.ser:
                self.root.after(0, self.enrollment_failed, 
                              "❌ Fingerprint sensor not connected!")
                return
            
            # Re-check sensor communication
            if not self.check_sensor():
                self.root.after(0, self.enrollment_failed,
                              "❌ Sensor communication lost!")
                return
            
            # Generate new fingerprint ID with NEW DATABASE STRUCTURE
            users = self.load_users()
            fingerprints = users.get("admin", {}).get("fingerprints", {})
            
            # Find next available ID (1-200 for AS608)
            new_id = None
            for i in range(1, 201):
                if str(i) not in fingerprints:
                    new_id = i
                    break
            
            if new_id is None:
                self.root.after(0, self.enrollment_failed, "Maximum fingerprints reached (200/200)")
                return
            
            self.current_enrollment_id = new_id
            
            # STEP 1: First fingerprint capture
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 1: Place finger FLAT on sensor...", 
                          10, "#00FF88", "#8A8DAB", "#8A8DAB")
            
            if not self.wait_for_fingerprint(timeout=25):
                self.root.after(0, self.enrollment_failed, 
                              "❌ No finger detected in Step 1!")
                return
            
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 1: Capturing fingerprint...", 
                          20, "#00FF88", "#00D4FF", "#8A8DAB")
            
            if not self.capture_fingerprint_with_retry(max_retries=5):
                self.root.after(0, self.enrollment_failed, 
                              "❌ Cannot capture fingerprint in Step 1!")
                return
            
            if not self.generate_character_file(1):
                self.root.after(0, self.enrollment_failed, 
                              "❌ Cannot process fingerprint image!")
                return
            
            self.root.after(0, self.update_enrollment_ui, 
                          "✅ First scan successful! Remove finger", 
                          30, "#00FF88", "#00FF88", "#8A8DAB")
            time.sleep(3)
            
            # STEP 2: Second fingerprint capture
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 2: Place the SAME finger again...\n💡 Use EXACT same position", 
                          40, "#00FF88", "#00FF88", "#8A8DAB")
            
            if not self.wait_for_fingerprint(timeout=25):
                self.root.after(0, self.enrollment_failed, 
                              "❌ No finger detected in Step 2!")
                return
            
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 2: Capturing fingerprint...", 
                          50, "#00FF88", "#00FF88", "#00D4FF")
            
            if not self.capture_fingerprint_with_retry(max_retries=5):
                self.root.after(0, self.enrollment_failed, 
                              "❌ Cannot capture second fingerprint!")
                return
            
            if not self.generate_character_file(2):
                self.root.after(0, self.enrollment_failed, 
                              "❌ Cannot process second fingerprint!")
                return
            
            self.root.after(0, self.update_enrollment_ui, 
                          "✅ Second scan successful!", 
                          60, "#00FF88", "#00FF88", "#00FF88")
            time.sleep(2)
            
            # STEP 3: Create template
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 3: Creating fingerprint template...", 
                          70, "#00FF88", "#00FF88", "#00FF88")
            
            if not self.create_template():
                self.root.after(0, self.enrollment_failed, 
                              "❌ Cannot create fingerprint template!\n\n💡 Fingers may not match. Please try again with more consistent placement.")
                return
            
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 3: Storing template...", 
                          80, "#00FF88", "#00FF88", "#00FF88")
            
            # Store template
            if not self.store_template(new_id):
                self.root.after(0, self.enrollment_failed, 
                              "❌ Cannot store fingerprint template!")
                return
            
            self.root.after(0, self.update_enrollment_ui, 
                          "✅ Template stored successfully!", 
                          90, "#00FF88", "#00FF88", "#00FF88")
            time.sleep(1)
            
            # 🆕 STEP 4: VERIFICATION TEST
            self.root.after(0, self.update_enrollment_ui, 
                          "STEP 4: VERIFICATION - Test fingerprint...", 
                          92, "#00FF88", "#00FF88", "#00FF88")
            
            print("✅ STEP 4: VERIFICATION - Test the new fingerprint")
            if not self.wait_for_fingerprint(timeout=15):
                self.root.after(0, self.update_enrollment_ui, 
                              "⚠️ Verification skipped - No finger detected", 
                              95, "#00FF88", "#00FF88", "#00FF88")
                # Still success, just no verification
                self.root.after(0, self.enrollment_success, new_id, 0)
                return
            
            if not self.capture_fingerprint_image():
                self.root.after(0, self.update_enrollment_ui, 
                              "⚠️ Verification skipped - Capture failed", 
                              95, "#00FF88", "#00FF88", "#00FF88")
                self.root.after(0, self.enrollment_success, new_id, 0)
                return
            
            if not self.generate_character_file(1):
                self.root.after(0, self.update_enrollment_ui, 
                              "⚠️ Verification skipped - Processing failed", 
                              95, "#00FF88", "#00FF88", "#00FF88")
                self.root.after(0, self.enrollment_success, new_id, 0)
                return
            
            # Search for the fingerprint we just enrolled
            success, template_id, score = self.search_fingerprint()
            
            if success and template_id == new_id:
                self.root.after(0, self.update_enrollment_ui, 
                              f"✅ VERIFICATION SUCCESS! Score: {score}", 
                              100, "#00FF88", "#00FF88", "#00FF88")
                time.sleep(2)
                self.root.after(0, self.enrollment_success, new_id, score)
            else:
                self.root.after(0, self.update_enrollment_ui, 
                              "⚠️ Verification failed - but enrollment completed", 
                              95, "#00FF88", "#00FF88", "#00FF88")
                self.root.after(0, self.enrollment_success, new_id, 0)
            
        except Exception as e:
            print(f"❌ Enrollment exception: {e}")
            self.root.after(0, self.enrollment_failed, f"System error: {str(e)}")

    def scan_fingerprint(self):
        """🆕 IMPROVED: Real-time fingerprint scanning with WORKING LOGIN METHOD"""
        if not self.fingerprint_connected or not self.ser:
            if hasattr(self, 'status_label'):
                self.status_label.config(text="❌ CONNECT FINGERPRINT SENSOR!", fg="#FF6B6B")
            return
        
        # Don't scan if already processing login or enrolling
        if self.login_processed or self.enrolling:
            return
        
        try:
            # 🆕 UPDATE UI: Show scanning status
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🔍 Scanning fingerprint...", fg="#00D4FF")
            
            # First check if finger is present
            if not self.wait_for_fingerprint(timeout=1):
                return
            
            # 🆕 UPDATE UI: Show capture status
            if hasattr(self, 'status_label'):
                self.status_label.config(text="📸 Capturing image...", fg="#00D4FF")
            
            # If finger is detected, capture image
            if not self.capture_fingerprint_image():
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="❌ Capture failed", fg="#FF6B6B")
                    self.root.after(2000, lambda: self.status_label.config(
                        text="PLACE FINGER ON SENSOR", 
                        fg="#8A8DAB"
                    ))
                return
            
            # 🆕 UPDATE UI: Show processing status
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🔄 Processing...", fg="#00D4FF")
            
            if not self.generate_character_file(1):
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="❌ Processing failed", fg="#FF6B6B")
                    self.root.after(2000, lambda: self.status_label.config(
                        text="PLACE FINGER ON SENSOR", 
                        fg="#8A8DAB"
                    ))
                return
            
            # 🆕 UPDATE UI: Show search status
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🔍 Searching database...", fg="#00D4FF")
            
            # 🆕 USE WORKING SEARCH METHOD
            success, fingerprint_id, match_score = self.search_fingerprint()
            
            # 🆕 CHECK SCORE THRESHOLD (from Second Code)
            if success and match_score > 100:
                # Check if enrolled in our system
                users = self.load_users()
                fingerprints = users.get("admin", {}).get("fingerprints", {})
                
                print(f"🔍 Checking fingerprint ID {fingerprint_id} against enrolled: {list(fingerprints.keys())}")
                
                if str(fingerprint_id) in fingerprints:
                    print(f"✅ ACCESS GRANTED! Fingerprint ID {fingerprint_id} recognized! Score: {match_score}")
                    
                    # 🆕 UPDATE UI: Show success with score
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"✅ VERIFIED! Score: {match_score}", fg="#00FF88")
                    
                    self.fingerprint_login_success()
                else:
                    print(f"❌ ACCESS DENIED! Fingerprint ID {fingerprint_id} not enrolled")
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text="❌ Fingerprint not enrolled", fg="#FF6B6B")
                        self.root.after(6000, lambda: self.status_label.config(
                            text="PLACE FINGER ON SENSOR", 
                            fg="#8A8DAB"
                        ))
            else:
                # No match found or low score
                if hasattr(self, 'status_label'):
                    if success and match_score <= 100:
                        self.status_label.config(text=f"❌ Low match score: {match_score}", fg="#FF6B6B")
                    else:
                        self.status_label.config(text="❌ Fingerprint not recognized", fg="#FF6B6B")
                    
                    self.root.after(6000, lambda: self.status_label.config(
                        text="PLACE FINGER ON SENSOR", 
                        fg="#8A8DAB"
                    ))
                    
        except Exception as e:
            print(f"❌ Fingerprint scan error: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="❌ Scan error - try again", fg="#FF6B6B")
                self.root.after(2000, lambda: self.status_label.config(
                    text="PLACE FINGER ON SENSOR", 
                    fg="#8A8DAB"
                ))

    def setup_security(self):
        """Initialize security system with NEW DATABASE STRUCTURE"""
        if not os.path.exists(self.users_file):
            default_users = {
                "admin": {
                    "password": self.hash_password("stimo123"),
                    "fingerprints": {},  # CHANGED: Now dictionary instead of list
                    "privilege": "admin"
                }
            }
            self.save_users(default_users)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_users(self, users_data):
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=4)
    
    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {"admin": {"fingerprints": {}, "password": self.hash_password("stimo123")}}

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_fingerprint_screen(self):
        """Show fingerprint scanning screen - RESPONSIVE VERSION OPTIMIZED FOR SMALL SCREENS"""
        self.clear_screen()
        self.current_screen = "fingerprint"
        self.login_processed = False
        self.enrolling = False
        
        # Main responsive container - REDUCED PADDING FOR SMALL SCREENS
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.03))

        # Status indicator - Responsive
        status_frame = tk.Frame(main_frame, bg='#0A0E29')
        status_frame.pack(pady=int(self.screen_height * 0.01))
        
        status_circle = tk.Label(
            status_frame,
            text="●" if self.fingerprint_connected else "○",
            font=("Arial", int(self.title_font_size * 1.2)),
            bg='#0A0E29',
            fg='#00FF88' if self.fingerprint_connected else '#FF6B6B'
        )
        status_circle.pack(side=tk.LEFT, padx=5)
        
        conn_label = tk.Label(
            status_frame,
            text=f"AS608: {'CONNECTED' if self.fingerprint_connected else 'DISCONNECTED'}",
            font=("Arial", self.small_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        conn_label.pack(side=tk.LEFT)
        
        # Reconnect button if disconnected
        if not self.fingerprint_connected:
            reconnect_btn = tk.Button(
                status_frame,
                text="🔄 Reconnect",
                font=("Arial", self.small_font_size),
                bg="#1E223D",
                fg="#00D4FF",
                relief="flat",
                command=self.reconnect_sensor
            )
            reconnect_btn.pack(side=tk.LEFT, padx=10)
        
        # Fingerprint icon - Responsive - REDUCED SIZE FOR SMALL SCREENS
        self.finger_icon = tk.Label(
            main_frame,
            text="👆",
            font=("Arial", self.large_icon_size),
            bg='#0A0E29',
            fg='#00FF88'
        )
        self.finger_icon.pack(pady=int(self.screen_height * 0.02))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="Fingerprint Authentication",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Status message
        if self.fingerprint_connected:
            status_text = "PLACE FINGER ON SENSOR"
            status_color = "#8A8DAB"
        else:
            status_text = "❌ AS608 NOT DETECTED"
            status_color = "#FF6B6B"
            
        self.status_label = tk.Label(
            main_frame,
            text=status_text,
            font=("Arial", self.normal_font_size),
            fg=status_color,
            bg='#0A0E29'
        )
        self.status_label.pack(pady=int(self.screen_height * 0.01))
        
        # 🆕 Score display label
        self.score_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", self.small_font_size),
            fg="#00D4FF",
            bg='#0A0E29'
        )
        self.score_label.pack(pady=int(self.screen_height * 0.005))
        
        # Progress bar - Responsive length
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=int(self.screen_width * 0.25)
        )
        self.progress.pack(pady=int(self.screen_height * 0.01))
        if self.fingerprint_connected:
            self.progress.start()
        
        # Buttons frame - Responsive layout - VERTICAL FOR SMALL SCREENS
        buttons_frame = tk.Frame(main_frame, bg='#0A0E29')
        buttons_frame.pack(pady=int(self.screen_height * 0.02))
        
        # Switch to password button - Responsive size
        switch_btn = tk.Button(
            buttons_frame,
            text="Use Password",
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.show_password_screen
        )
        switch_btn.pack(pady=int(self.screen_height * 0.005))
        
        # Add fingerprint button - Responsive size
        add_fp_btn = tk.Button(
            buttons_frame,
            text="➕ Add Fingerprint",
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.show_password_for_enrollment
        )
        add_fp_btn.pack(pady=int(self.screen_height * 0.005))

    def reconnect_sensor(self):
        """Attempt to reconnect to fingerprint sensor"""
        self.status_label.config(text="🔄 Attempting to reconnect sensor...", fg="#00D4FF")
        self.root.update()
        
        if self.initialize_as608_with_retry():
            self.show_fingerprint_screen()
        else:
            self.status_label.config(text="❌ Reconnection failed!", fg="#FF6B6B")

    def start_fingerprint_scanning(self):
        """Start continuous fingerprint scanning"""
        def scan_loop():
            while True:
                if (self.current_screen == "fingerprint" and 
                    not self.enrolling and 
                    not self.login_processed and
                    self.fingerprint_connected):
                    self.scan_fingerprint()
                time.sleep(1.0)
        
        scan_thread = threading.Thread(target=scan_loop, daemon=True)
        scan_thread.start()

    def fingerprint_login_success(self):
        """Handle successful fingerprint login"""
        if self.login_processed:
            return
            
        self.login_processed = True
        
        # Update UI in main thread
        self.root.after(0, self._update_ui_for_success)
        
        # Launch STIMO system after 2 seconds
        self.root.after(2000, self.launch_stimo_system)

    def _update_ui_for_success(self):
        """Update UI for successful login (called in main thread)"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text="✅ FINGERPRINT VERIFIED! WELCOME!", fg="#00FF88")
        
        if hasattr(self, 'progress'):
            self.progress.stop()
        
        # Update UI to show success
        if hasattr(self, 'finger_icon'):
            self.finger_icon.config(text="✅", fg="#00FF88")

    def show_password_screen(self):
        """Show password login screen - RESPONSIVE VERSION OPTIMIZED FOR SMALL SCREENS"""
        self.clear_screen()
        self.current_screen = "password"
        
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.02))
        
        # Back button - Responsive
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back to Fingerprint",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_fingerprint_screen
        )
        back_btn.pack(anchor='nw', pady=(0, int(self.screen_height * 0.01)))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="Password Authentication",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Password label - Responsive
        pass_label = tk.Label(
            main_frame,
            text="Enter Password:",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        pass_label.pack(pady=(int(self.screen_height * 0.02), int(self.screen_height * 0.005)))
        
        # Password entry - Responsive
        self.pass_entry = tk.Entry(
            main_frame,
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="white",
            show="•",
            relief="flat",
            width=max(15, int(self.screen_width * 0.008)),
            justify='center'
        )
        self.pass_entry.pack(pady=(0, int(self.screen_height * 0.01)))
        self.pass_entry.bind('<Return>', lambda e: self.authenticate_password())
        
        # Buttons frame - Responsive - VERTICAL FOR SMALL SCREENS
        buttons_frame = tk.Frame(main_frame, bg='#0A0E29')
        buttons_frame.pack(pady=int(self.screen_height * 0.02))
        
        # Login button - Responsive
        login_btn = tk.Button(
            buttons_frame,
            text="Login to STIMO",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#00FF88",
            fg="#0A0E29",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.authenticate_password
        )
        login_btn.pack(pady=int(self.screen_height * 0.005))
        
        # Add fingerprint button - Responsive
        add_fp_btn = tk.Button(
            buttons_frame,
            text="➕ Add Fingerprint",
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.show_password_for_enrollment
        )
        add_fp_btn.pack(pady=int(self.screen_height * 0.005))
        
        # On-screen Keyboard Frame - Responsive - SMALLER FOR SMALL SCREENS
        self.create_onscreen_keyboard(main_frame, self.pass_entry, self.authenticate_password)

    def show_password_for_enrollment(self):
        """Show password screen for fingerprint enrollment access - RESPONSIVE OPTIMIZED"""
        self.clear_screen()
        self.current_screen = "password_enrollment"
        
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.03))
        
        # Back button - Responsive
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_fingerprint_screen
        )
        back_btn.pack(anchor='nw', pady=(0, int(self.screen_height * 0.02)))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="Admin Authentication Required",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Security icon - Responsive
        security_icon = tk.Label(
            main_frame,
            text="🔒",
            font=("Arial", self.large_icon_size),
            bg='#0A0E29',
            fg="#00D4FF"
        )
        security_icon.pack(pady=int(self.screen_height * 0.02))
        
        # Instructions - Responsive
        instruction_label = tk.Label(
            main_frame,
            text="Enter admin password to access fingerprint enrollment",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        instruction_label.pack(pady=int(self.screen_height * 0.01))
        
        # Password label - Responsive
        pass_label = tk.Label(
            main_frame,
            text="Admin Password:",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        pass_label.pack(pady=(int(self.screen_height * 0.02), int(self.screen_height * 0.005)))
        
        # Password entry - Responsive
        self.enroll_pass_entry = tk.Entry(
            main_frame,
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="white",
            show="•",
            relief="flat",
            width=max(15, int(self.screen_width * 0.008)),
            justify='center'
        )
        self.enroll_pass_entry.pack(pady=(0, int(self.screen_height * 0.02)))
        self.enroll_pass_entry.bind('<Return>', lambda e: self.authenticate_enrollment_password())
        self.enroll_pass_entry.focus_set()
        
        # Authenticate button - Responsive
        auth_btn = tk.Button(
            main_frame,
            text="Authenticate",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#00FF88",
            fg="#0A0E29",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.authenticate_enrollment_password
        )
        auth_btn.pack(pady=int(self.screen_height * 0.01))
        
        # On-screen Keyboard Frame - Responsive
        self.create_onscreen_keyboard(main_frame, self.enroll_pass_entry, self.authenticate_enrollment_password)

    def authenticate_enrollment_password(self):
        """Authenticate password for enrollment access"""
        password = self.enroll_pass_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter admin password")
            return
            
        users = self.load_users()
        
        password_valid = False
        for username, user_data in users.items():
            hashed_input = self.hash_password(password)
            if user_data["password"] == hashed_input:
                password_valid = True
                break
        
        if password_valid:
            messagebox.showinfo("Success", "Admin authenticated! Access granted to fingerprint enrollment.")
            self.show_admin_menu_screen()
        else:
            messagebox.showerror("Error", "Invalid admin password")

    def authenticate_password(self):
        """Authenticate using password only"""
        password = self.pass_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
            
        users = self.load_users()
        
        password_valid = False
        for username, user_data in users.items():
            hashed_input = self.hash_password(password)
            if user_data["password"] == hashed_input:
                password_valid = True
                break
        
        if password_valid:
            messagebox.showinfo("Success", "Password verified! Welcome to STIMO!")
            self.launch_stimo_system()
        else:
            messagebox.showerror("Error", "Invalid password")

    def show_admin_menu_screen(self):
        """Show admin menu - RESPONSIVE VERSION OPTIMIZED FOR SMALL SCREENS"""
        self.clear_screen()
        self.current_screen = "admin_menu"
        
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.03))
        
        # Back button - Responsive
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_fingerprint_screen
        )
        back_btn.pack(anchor='nw', pady=(0, int(self.screen_height * 0.02)))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="Admin Menu",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Admin icon - Responsive
        admin_icon = tk.Label(
            main_frame,
            text="⚙️",
            font=("Arial", self.large_icon_size),
            bg='#0A0E29',
            fg="#00D4FF"
        )
        admin_icon.pack(pady=int(self.screen_height * 0.02))
        
        # Buttons frame - Responsive - VERTICAL FOR SMALL SCREENS
        buttons_frame = tk.Frame(main_frame, bg='#0A0E29')
        buttons_frame.pack(pady=int(self.screen_height * 0.03))
        
        # Add Fingerprint button - Responsive
        add_fp_btn = tk.Button(
            buttons_frame,
            text="➕ Add Fingerprint",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=max(18, int(self.screen_width * 0.01)),
            height=self.button_height,
            command=self.show_add_fingerprint_screen
        )
        add_fp_btn.pack(pady=int(self.screen_height * 0.008))
        
        # Manage Fingerprints button - Responsive
        manage_fp_btn = tk.Button(
            buttons_frame,
            text="👆 Manage Fingerprints",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=max(18, int(self.screen_width * 0.01)),
            height=self.button_height,
            command=self.show_manage_fingerprints_screen
        )
        manage_fp_btn.pack(pady=int(self.screen_height * 0.008))
        
        # Change Password button - Responsive
        change_pass_btn = tk.Button(
            buttons_frame,
            text="🔑 Change Password",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=max(18, int(self.screen_width * 0.01)),
            height=self.button_height,
            command=self.show_change_password_screen
        )
        change_pass_btn.pack(pady=int(self.screen_height * 0.008))
        
        # 🆕 System Status button - Responsive
        status_btn = tk.Button(
            buttons_frame,
            text="📊 System Status",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#1E223D",
            fg="#00D4FF",
            relief="flat",
            width=max(18, int(self.screen_width * 0.01)),
            height=self.button_height,
            command=self.show_system_status_screen
        )
        status_btn.pack(pady=int(self.screen_height * 0.008))

    def show_add_fingerprint_screen(self):
        """Show add fingerprint enrollment screen - RESPONSIVE VERSION OPTIMIZED FOR SMALL SCREENS"""
        self.clear_screen()
        self.current_screen = "add_fingerprint"
        self.enrolling = True
        self.enrollment_step = 0
        
        # Check if maximum fingerprints reached
        users = self.load_users()
        fingerprints = users.get("admin", {}).get("fingerprints", {})
        
        if len(fingerprints) >= 200:
            messagebox.showerror("Error", "Maximum 200 fingerprints reached! Please delete some fingerprints first.")
            self.show_admin_menu_screen()
            return
        
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.02))
        
        # Back button - Responsive
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back to Admin Menu",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_admin_menu_screen
        )
        back_btn.pack(anchor='nw', pady=(0, int(self.screen_height * 0.02)))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="Add New Fingerprint",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Current fingerprints info - Responsive
        users = self.load_users()
        fingerprints = users.get("admin", {}).get("fingerprints", {})
        info_label = tk.Label(
            main_frame,
            text=f"Currently enrolled: {len(fingerprints)}/200 fingerprints",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        info_label.pack(pady=int(self.screen_height * 0.005))
        
        # 🆕 ENROLLMENT TIPS - Responsive
        tips_label = tk.Label(
            main_frame,
            text="💡 TIPS: Place finger FLAT • Apply firm pressure • Keep finger CLEAN • Use SAME position",
            font=("Arial", self.small_font_size),
            fg="#00D4FF",
            bg='#0A0E29',
            wraplength=int(self.screen_width * 0.8)
        )
        tips_label.pack(pady=int(self.screen_height * 0.005))
        
        # Fingerprint icon - Responsive
        self.enroll_icon = tk.Label(
            main_frame,
            text="👆",
            font=("Arial", self.large_icon_size),
            bg='#0A0E29',
            fg='#00D4FF'
        )
        self.enroll_icon.pack(pady=int(self.screen_height * 0.02))
        
        # Instructions - Responsive
        self.instruction_label = tk.Label(
            main_frame,
            text="Click 'Start Enrollment' and place your finger on the scanner\nStep 1 of 4",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29',
            justify='center'
        )
        self.instruction_label.pack(pady=int(self.screen_height * 0.01))
        
        # Progress frame - Responsive
        progress_frame = tk.Frame(main_frame, bg='#0A0E29')
        progress_frame.pack(pady=int(self.screen_height * 0.01))
        
        # Progress indicators - 🆕 NOW 4 STEPS - Responsive
        self.step1 = tk.Label(progress_frame, text="●", font=("Arial", int(self.title_font_size * 0.8)), fg="#8A8DAB", bg='#0A0E29')
        self.step1.pack(side=tk.LEFT, padx=int(self.screen_width * 0.003))
        self.step2 = tk.Label(progress_frame, text="○", font=("Arial", int(self.title_font_size * 0.8)), fg="#8A8DAB", bg='#0A0E29')
        self.step2.pack(side=tk.LEFT, padx=int(self.screen_width * 0.003))
        self.step3 = tk.Label(progress_frame, text="○", font=("Arial", int(self.title_font_size * 0.8)), fg="#8A8DAB", bg='#0A0E29')
        self.step3.pack(side=tk.LEFT, padx=int(self.screen_width * 0.003))
        self.step4 = tk.Label(progress_frame, text="○", font=("Arial", int(self.title_font_size * 0.8)), fg="#8A8DAB", bg='#0A0E29')  # 🆕 STEP 4
        self.step4.pack(side=tk.LEFT, padx=int(self.screen_width * 0.003))
        
        # Enrollment progress bar - Responsive
        self.enroll_progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=int(self.screen_width * 0.3)
        )
        self.enroll_progress.pack(pady=int(self.screen_height * 0.01))
        
        # Status message - Responsive
        self.enroll_status = tk.Label(
            main_frame,
            text="Ready to enroll new fingerprint...",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        self.enroll_status.pack(pady=int(self.screen_height * 0.01))
        
        # Start enrollment button - Responsive
        self.start_enroll_btn = tk.Button(
            main_frame,
            text="Start Enrollment",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#00FF88",
            fg="#0A0E29",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.start_fingerprint_enrollment
        )
        self.start_enroll_btn.pack(pady=int(self.screen_height * 0.01))
        
        # Cancel button - Responsive
        cancel_btn = tk.Button(
            main_frame,
            text="Cancel",
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="#FF6B6B",
            relief="flat",
            width=max(10, int(self.screen_width * 0.005)),
            height=self.button_height,
            command=self.show_admin_menu_screen
        )
        cancel_btn.pack(pady=int(self.screen_height * 0.005))

    def start_fingerprint_enrollment(self):
        """Start the fingerprint enrollment process"""
        self.start_enroll_btn.config(state='disabled')
        self.enroll_status.config(text="Starting REAL fingerprint enrollment...")
        
        enroll_thread = threading.Thread(target=self.enroll_fingerprint, daemon=True)
        enroll_thread.start()

    def enrollment_success(self, new_id, score):
        """Handle successful enrollment with NEW DATABASE STRUCTURE"""
        # Save new fingerprint to users file with NEW STRUCTURE
        users = self.load_users()
        if "admin" not in users:
            users["admin"] = {}
        if "fingerprints" not in users["admin"]:
            users["admin"]["fingerprints"] = {}
        
        # 🆕 NEW DATABASE STRUCTURE
        users["admin"]["fingerprints"][str(new_id)] = {
            "enrollment_date": time.time(),
            "base_score": score if score > 0 else 500
        }
        self.save_users(users)
        
        if score > 0:
            self.enroll_status.config(text=f"✅ FINGERPRINT ENROLLED & VERIFIED! (ID: {new_id}, Score: {score})", fg="#00FF88")
        else:
            self.enroll_status.config(text=f"✅ FINGERPRINT ENROLLED! (ID: {new_id})", fg="#00FF88")
        
        self.enroll_icon.config(text="✅", fg="#00FF88")
        
        # Show success message
        if score > 0:
            messagebox.showinfo("Success", f"FINGERPRINT ENROLLED & VERIFIED!\n\nFingerprint ID: {new_id}\nMatch Score: {score}\n\nYou can now use this fingerprint to login.")
        else:
            messagebox.showinfo("Success", f"FINGERPRINT ENROLLED!\n\nFingerprint ID: {new_id}\n\nYou can now use this fingerprint to login.")
        
        # Go back to admin menu
        self.root.after(2000, self.show_admin_menu_screen)

    def update_enrollment_ui(self, message, progress, step1_color, step2_color, step3_color):
        """Update the enrollment UI"""
        self.instruction_label.config(text=message)
        self.enroll_progress['value'] = progress
        self.step1.config(fg=step1_color)
        self.step2.config(fg=step2_color)
        self.step3.config(fg=step3_color)
        # Step 4 will be handled separately for verification

    def enrollment_failed(self, error_message):
        """Handle enrollment failure with BETTER ERROR GUIDANCE"""
        self.enroll_status.config(text=f"❌ Enrollment failed: {error_message}", fg="#FF6B6B")
        self.enroll_icon.config(text="❌", fg="#FF6B6B")
        self.start_enroll_btn.config(state='normal')
        
        # Show error message with GUIDANCE
        if "don't match" in error_message.lower():
            guidance = "\n💡 Possible reasons:\n• Different finger positions\n• Too much pressure variation\n• Finger not clean enough\n• Try enrolling a different finger"
            messagebox.showerror("Enrollment Failed", f"Fingerprint enrollment failed:\n{error_message}{guidance}")
        else:
            messagebox.showerror("Enrollment Failed", f"Fingerprint enrollment failed:\n{error_message}\n\nPlease try again.")

    def show_manage_fingerprints_screen(self):
        """Show screen to manage enrolled fingerprints with NEW DATABASE STRUCTURE - RESPONSIVE OPTIMIZED"""
        self.clear_screen()
        self.current_screen = "manage_fingerprints"
        
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.02))
        
        # Back button - Responsive
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back to Admin Menu",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_admin_menu_screen
        )
        back_btn.pack(anchor='nw', pady=(0, int(self.screen_height * 0.01)))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="Manage Fingerprints",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Load current fingerprints with NEW STRUCTURE
        users = self.load_users()
        fingerprints = users.get("admin", {}).get("fingerprints", {})
        
        # Fingerprints count - Responsive
        count_label = tk.Label(
            main_frame,
            text=f"Enrolled Fingerprints: {len(fingerprints)}/200",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        count_label.pack(pady=int(self.screen_height * 0.01))
        
        # Create scrollable frame for fingerprints - Responsive - SMALLER FOR SMALL SCREENS
        canvas = tk.Canvas(main_frame, bg='#0A0E29', highlightthickness=0, height=int(self.screen_height * 0.5))
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#0A0E29')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display fingerprints with NEW DATA - Responsive
        if fingerprints:
            for fp_id, fp_data in fingerprints.items():
                fp_frame = tk.Frame(scrollable_frame, bg='#1E223D', relief='flat', bd=1)
                fp_frame.pack(fill='x', padx=int(self.screen_width * 0.005), pady=int(self.screen_height * 0.003))
                
                # 🆕 SHOW ENROLLMENT DATE AND SCORE
                enroll_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(fp_data.get('enrollment_date', 0)))
                base_score = fp_data.get('base_score', 'N/A')
                
                fp_label = tk.Label(
                    fp_frame,
                    text=f"Fingerprint ID: {fp_id} | Enrolled: {enroll_date} | Score: {base_score}",
                    font=("Arial", self.small_font_size),
                    fg="#FFFFFF",
                    bg='#1E223D'
                )
                fp_label.pack(side=tk.LEFT, padx=int(self.screen_width * 0.005), pady=int(self.screen_height * 0.005))
                
                delete_btn = tk.Button(
                    fp_frame,
                    text="🗑️ Delete",
                    font=("Arial", self.small_font_size),
                    bg="#FF6B6B",
                    fg="#FFFFFF",
                    relief="flat",
                    command=lambda fid=fp_id: self.delete_fingerprint(fid)
                )
                delete_btn.pack(side=tk.RIGHT, padx=int(self.screen_width * 0.005), pady=int(self.screen_height * 0.003))
        else:
            no_fp_label = tk.Label(
                scrollable_frame,
                text="No fingerprints enrolled yet",
                font=("Arial", self.normal_font_size),
                fg="#8A8DAB",
                bg='#0A0E29'
            )
            no_fp_label.pack(pady=int(self.screen_height * 0.03))
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, int(self.screen_width * 0.003)))
        scrollbar.pack(side="right", fill="y")
        
        # Set canvas scroll region
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def delete_fingerprint(self, fingerprint_id):
        """Delete a fingerprint from both system and AS608 module"""
        users = self.load_users()
        if "admin" in users and "fingerprints" in users["admin"]:
            if fingerprint_id in users["admin"]["fingerprints"]:
                # Delete from AS608 module if connected
                if self.fingerprint_connected and self.ser:
                    try:
                        # PS_DeletChar command
                        fid_int = int(fingerprint_id)
                        delete_cmd = bytes([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x07, 0x0C, 0x00, 0x00, (fid_int >> 8) & 0xFF, fid_int & 0xFF, 0x00])
                        # Calculate checksum
                        data = delete_cmd[6:]
                        checksum = (sum(data) & 0xFF)
                        delete_cmd = delete_cmd + bytes([checksum])
                        
                        self.ser.write(delete_cmd)
                        time.sleep(1.0)
                        response = self.ser.read(12)
                        if response and response[9] == 0x00:
                            print(f"✅ Fingerprint ID {fingerprint_id} deleted from AS608")
                        else:
                            print(f"⚠️ Could not delete fingerprint from AS608")
                    except Exception as e:
                        print(f"❌ Error deleting from AS608: {e}")
                
                # Delete from our system
                del users["admin"]["fingerprints"][fingerprint_id]
                self.save_users(users)
                messagebox.showinfo("Success", f"Fingerprint ID {fingerprint_id} deleted successfully!")
                self.show_manage_fingerprints_screen()
            else:
                messagebox.showerror("Error", "Fingerprint not found!")
        else:
            messagebox.showerror("Error", "No fingerprints found!")

    def show_system_status_screen(self):
        """🆕 NEW: Show system status screen - RESPONSIVE OPTIMIZED"""
        self.clear_screen()
        self.current_screen = "system_status"
        
        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.02))
        
        # Back button - Responsive
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back to Admin Menu",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_admin_menu_screen
        )
        back_btn.pack(anchor='nw', pady=(0, int(self.screen_height * 0.01)))
        
        # Title - Responsive
        title_label = tk.Label(
            main_frame,
            text="System Status",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.pack(pady=int(self.screen_height * 0.01))
        
        # Status icon - Responsive
        status_icon = tk.Label(
            main_frame,
            text="📊",
            font=("Arial", self.large_icon_size),
            bg='#0A0E29',
            fg="#00D4FF"
        )
        status_icon.pack(pady=int(self.screen_height * 0.02))
        
        # Load current data
        users = self.load_users()
        fingerprints = users.get("admin", {}).get("fingerprints", {})
        
        # Status information - Responsive
        info_frame = tk.Frame(main_frame, bg='#0A0E29')
        info_frame.pack(pady=int(self.screen_height * 0.03), fill='x')
        
        # Sensor status - Responsive
        sensor_status = "✅ CONNECTED" if self.fingerprint_connected else "❌ DISCONNECTED"
        sensor_label = tk.Label(
            info_frame,
            text=f"Fingerprint Sensor: {sensor_status}",
            font=("Arial", self.normal_font_size),
            fg="#00FF88" if self.fingerprint_connected else "#FF6B6B",
            bg='#0A0E29'
        )
        sensor_label.pack(pady=int(self.screen_height * 0.005))
        
        # Fingerprint count - Responsive
        count_label = tk.Label(
            info_frame,
            text=f"Enrolled Fingerprints: {len(fingerprints)}/200",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        count_label.pack(pady=int(self.screen_height * 0.005))
        
        # Database status - Responsive
        db_label = tk.Label(
            info_frame,
            text=f"Database File: {self.users_file}",
            font=("Arial", self.small_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        db_label.pack(pady=int(self.screen_height * 0.005))
        
        # Show fingerprint IDs if any - Responsive
        if fingerprints:
            ids_label = tk.Label(
                info_frame,
                text=f"Fingerprint IDs: {', '.join(sorted(fingerprints.keys()))}",
                font=("Arial", self.small_font_size),
                fg="#00D4FF",
                bg='#0A0E29',
                wraplength=int(self.screen_width * 0.8)
            )
            ids_label.pack(pady=int(self.screen_height * 0.01))

    def show_change_password_screen(self):
        """Show change password screen - responsive two-column layout so keyboard fits"""
        self.clear_screen()
        self.current_screen = "change_password"

        main_frame = tk.Frame(self.root, bg='#0A0E29')
        main_frame.pack(expand=True, fill='both', padx=int(self.screen_width * 0.03), pady=int(self.screen_height * 0.02))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        # Back button - keep at top-left
        back_btn = tk.Button(
            main_frame,
            text="🔙 Back to Admin Menu",
            font=("Arial", self.small_font_size),
            bg='#0A0E29',
            fg="#00D4FF",
            relief="flat",
            command=self.show_admin_menu_screen
        )
        back_btn.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, int(self.screen_height * 0.01)))

        # Title centered
        title_label = tk.Label(
            main_frame,
            text="Change Password",
            font=("Arial", self.title_font_size, "bold"),
            fg="#FFFFFF",
            bg='#0A0E29'
        )
        title_label.grid(row=1, column=0, columnspan=2, pady=int(self.screen_height * 0.01))

        # Password icon (optional) above the form
        password_icon = tk.Label(
            main_frame,
            text="🔑",
            font=("Arial", self.large_icon_size),
            bg='#0A0E29',
            fg="#00D4FF"
        )
        password_icon.grid(row=2, column=0, columnspan=2, pady=int(self.screen_height * 0.01))

        # Create a content frame for the two-column layout
        form_frame = tk.Frame(main_frame, bg='#0A0E29')
        form_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=int(self.screen_height * 0.01))

        # Configure grid weights so columns expand evenly
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Current Password (left column)
        current_pass_label = tk.Label(
            form_frame,
            text="Current Password:",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        current_pass_label.grid(row=0, column=0, sticky='w', padx=int(self.screen_width * 0.01), pady=(0, int(self.screen_height * 0.005)))

        self.current_pass_entry = tk.Entry(
            form_frame,
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="white",
            show="•",
            relief="flat",
            width=max(15, int(self.screen_width * 0.008)),
            justify='center'
        )
        self.current_pass_entry.grid(row=1, column=0, sticky='ew', padx=int(self.screen_width * 0.01))

        # New Password (right column)
        new_pass_label = tk.Label(
            form_frame,
            text="New Password:",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        new_pass_label.grid(row=0, column=1, sticky='w', padx=int(self.screen_width * 0.01), pady=(0, int(self.screen_height * 0.005)))

        self.new_pass_entry = tk.Entry(
            form_frame,
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="white",
            show="•",
            relief="flat",
            width=max(15, int(self.screen_width * 0.008)),
            justify='center'
        )
        self.new_pass_entry.grid(row=1, column=1, sticky='ew', padx=int(self.screen_width * 0.01))

        # Confirm New Password - full width below
        confirm_pass_label = tk.Label(
            form_frame,
            text="Confirm New Password:",
            font=("Arial", self.normal_font_size),
            fg="#8A8DAB",
            bg='#0A0E29'
        )
        confirm_pass_label.grid(row=2, column=0, columnspan=2, sticky='w', padx=int(self.screen_width * 0.01), pady=(int(self.screen_height * 0.01), int(self.screen_height * 0.005)))

        self.confirm_pass_entry = tk.Entry(
            form_frame,
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="white",
            show="•",
            relief="flat",
            width=max(20, int(self.screen_width * 0.016)),
            justify='center'
        )
        self.confirm_pass_entry.grid(row=3, column=0, columnspan=2, sticky='ew', padx=int(self.screen_width * 0.01))

        # Set initial focus
        self.current_focused_entry = self.current_pass_entry
        self.current_pass_entry.focus_set()

        # Buttons frame under the form (still above keyboard)
        btns_frame = tk.Frame(main_frame, bg='#0A0E29')
        btns_frame.grid(row=4, column=0, columnspan=2, pady=int(self.screen_height * 0.01))

        change_btn = tk.Button(
            btns_frame,
            text="Change Password",
            font=("Arial", self.normal_font_size, "bold"),
            bg="#00FF88",
            fg="#0A0E29",
            relief="flat",
            width=self.button_width,
            height=self.button_height,
            command=self.change_password
        )
        change_btn.pack(side='left', padx=8)

        cancel_btn = tk.Button(
            btns_frame,
            text="Cancel",
            font=("Arial", self.normal_font_size),
            bg="#1E223D",
            fg="#FF6B6B",
            relief="flat",
            width=max(10, int(self.screen_width * 0.005)),
            height=self.button_height,
            command=self.show_admin_menu_screen
        )
        cancel_btn.pack(side='left', padx=8)

           # --- place keyboard inside its own bottom frame so pack() inside keyboard works ---
        bottom_frame = tk.Frame(main_frame, bg='#0A0E29')
        # put bottom_frame as last grid row; adjust pady if needed
        bottom_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(int(self.screen_height * 0.005), 0))

        try:
            # Use bottom_frame as parent so the keyboard's pack() won't conflict with main_frame's grid()
            self.create_onscreen_keyboard_for_multiple_fields(bottom_frame, self.change_password)
        except Exception as e:
            # fallback: single-field keyboard (some versions expect (parent, target_entry, enter_command))
            try:
                self.create_onscreen_keyboard(bottom_frame, self.confirm_pass_entry, self.change_password)
            except Exception as e2:
                print("⚠️ Keyboard creation fallback failed:", e, e2)


    def change_password(self):
        """Change the admin password"""
        current_password = self.current_pass_entry.get()
        new_password = self.new_pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match")
            return
            
        if len(new_password) < 4:
            messagebox.showerror("Error", "New password must be at least 4 characters")
            return
            
        users = self.load_users()
        
        # Verify current password
        current_password_valid = False
        for username, user_data in users.items():
            hashed_current = self.hash_password(current_password)
            if user_data["password"] == hashed_current:
                current_password_valid = True
                # Update password
                users[username]["password"] = self.hash_password(new_password)
                break
        
        if current_password_valid:
            self.save_users(users)
            messagebox.showinfo("Success", "Password changed successfully!")
            self.show_admin_menu_screen()
        else:
            messagebox.showerror("Error", "Current password is incorrect")

    def create_onscreen_keyboard(self, parent, target_entry, enter_command):
        """Create on-screen keyboard - RESPONSIVE VERSION OPTIMIZED FOR SMALL SCREENS"""
        keyboard_frame = tk.Frame(parent, bg='#0A0E29')
        keyboard_frame.pack(pady=int(self.screen_height * 0.01), fill='x')
        
        # Keyboard layout
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '⌫'],
            ['Space', 'Clear', 'Enter']
        ]
        
        # Calculate button sizes based on screen - SMALLER FOR SMALL SCREENS
        key_width = max(2, int(self.screen_width * 0.004))
        key_height = 1
        large_key_width = max(6, int(self.screen_width * 0.008))
        
        # Create keyboard buttons
        for i, row in enumerate(rows):
            row_frame = tk.Frame(keyboard_frame, bg='#0A0E29')
            row_frame.pack(pady=int(self.screen_height * 0.002))
            
            for j, key in enumerate(row):
                if key == 'Space':
                    btn_width = large_key_width
                    bg_color = '#1E223D'
                elif key == 'Clear':
                    btn_width = key_width + 1
                    bg_color = '#FF6B6B'
                elif key == 'Enter':
                    btn_width = key_width + 1
                    bg_color = '#00FF88'
                elif key == '⌫':
                    btn_width = key_width
                    bg_color = '#FFA500'
                else:
                    btn_width = key_width
                    bg_color = '#1E223D'
                
                btn = tk.Button(
                    row_frame,
                    text=key,
                    font=("Arial", self.small_font_size, "bold"),
                    bg=bg_color,
                    fg="white",
                    relief="flat",
                    width=btn_width,
                    height=key_height,
                    command=lambda k=key, t=target_entry, e=enter_command: self.keyboard_press(k, t, e)
                )
                btn.pack(side=tk.LEFT, padx=int(self.screen_width * 0.001))

    def keyboard_press(self, key, target_entry, enter_command):
        """Handle keyboard button presses"""
        current_text = target_entry.get()
        
        if key == '⌫':  # Backspace
            target_entry.delete(len(current_text)-1, tk.END)
        elif key == 'Clear':
            target_entry.delete(0, tk.END)
        elif key == 'Space':
            target_entry.insert(tk.END, ' ')
        elif key == 'Enter':
            enter_command()
        else:
            target_entry.insert(tk.END, key)

    def create_onscreen_keyboard_for_multiple_fields(self, parent, enter_command):
        """Create on-screen keyboard for multiple fields - RESPONSIVE OPTIMIZED"""
        keyboard_frame = tk.Frame(parent, bg='#0A0E29')
        keyboard_frame.pack(pady=int(self.screen_height * 0.01), fill='x')
        
        # Keyboard layout
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '⌫'],
            ['Space', 'Clear', 'Enter']
        ]
        
        # Calculate button sizes based on screen - SMALLER FOR SMALL SCREENS
        key_width = max(2, int(self.screen_width * 0.004))
        key_height = 1
        large_key_width = max(6, int(self.screen_width * 0.008))
        
        # Create keyboard buttons
        for i, row in enumerate(rows):
            row_frame = tk.Frame(keyboard_frame, bg='#0A0E29')
            row_frame.pack(pady=int(self.screen_height * 0.002))
            
            for j, key in enumerate(row):
                if key == 'Space':
                    btn_width = large_key_width
                    bg_color = '#1E223D'
                elif key == 'Clear':
                    btn_width = key_width + 1
                    bg_color = '#FF6B6B'
                elif key == 'Enter':
                    btn_width = key_width + 1
                    bg_color = '#00FF88'
                elif key == '⌫':
                    btn_width = key_width
                    bg_color = '#FFA500'
                else:
                    btn_width = key_width
                    bg_color = '#1E223D'
                
                btn = tk.Button(
                    row_frame,
                    text=key,
                    font=("Arial", self.small_font_size, "bold"),
                    bg=bg_color,
                    fg="white",
                    relief="flat",
                    width=btn_width,
                    height=key_height,
                    command=lambda k=key, e=enter_command: self.keyboard_press_multiple_fields(k, e)
                )
                btn.pack(side=tk.LEFT, padx=int(self.screen_width * 0.001))

    def keyboard_press_multiple_fields(self, key, enter_command):
        """Handle keyboard button presses for multiple fields"""
        if self.current_focused_entry is None:
            return
            
        current_text = self.current_focused_entry.get()
        
        if key == '⌫':  # Backspace
            self.current_focused_entry.delete(len(current_text)-1, tk.END)
        elif key == 'Clear':
            self.current_focused_entry.delete(0, tk.END)
        elif key == 'Space':
            self.current_focused_entry.insert(tk.END, ' ')
        elif key == 'Enter':
            enter_command()
        else:
            self.current_focused_entry.insert(tk.END, key)


    def launch_stimo_system(self):
        """Signal preloaded STIMO to show after fingerprint success"""
        try:
            # Drop trigger file to wake main.py
            trigger_file = "/home/stimo/STIMO_Mode/start_trigger.txt"
            with open(trigger_file, "w") as f:
                f.write("start")

            print("🚀 Trigger sent to STIMO, fingerprint closing...")
            self.root.destroy()
        except Exception as e:
            print(f"❌ Failed to trigger STIMO system: {e}")


    def run(self):
        """Start the application"""
        self.root.mainloop()
        
 

        
        

# Run the application
if __name__ == "__main__":
    app = STIMOFingerprintAuth()
    app.run()