import os
import random
import time
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox

class RealUserAgentRotator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🔄 Real User-Agent Rotator")
        self.root.geometry("900x700")
        
        # System control variables
        self.rotation_active = False
        self.current_ua = ""
        self.rotation_interval = 30
        self.lock_gui = False
        
        # Directories and files
        self.ua_dir = "/home/god/Desktop/APLIKASI/data/proteksi/useragent/"
        self.temp_ua_file = "/tmp/current_ua.txt"
        self.proxy_config_file = "/etc/proxychains.conf"
        
        # Initialize
        self.load_user_agents()
        self.setup_gui()
        
    def setup_gui(self):
        # Configure main grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self.root, height=70)
        header.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(header, 
                    text="🔄 REAL User-Agent Rotation System",
                    font=("Arial", 20, "bold")).pack(pady=10)
        
        # Main content
        content = ctk.CTkFrame(self.root)
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)
        
        # User-Agent display
        self.ua_display = ctk.CTkTextbox(content, height=100, wrap="word")
        self.ua_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.update_ua_display()
        
        # UA list with scroll
        self.ua_list = ctk.CTkTextbox(content, wrap="none", font=("Consolas", 11))
        self.ua_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        scrollbar = ctk.CTkScrollbar(content, command=self.ua_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.ua_list.configure(yscrollcommand=scrollbar.set)
        self.refresh_ua_list()
        
        # Button panel
        btn_panel = ctk.CTkFrame(content)
        btn_panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        buttons = [
            ("📁 Import UA", self.import_ua, "#1565C0"),
            ("✏️ Add Manual", self.add_manual_ua, "#00796B"),
            ("🗑️ Delete UA", self.delete_ua, "#D32F2F"),
            ("⚙️ Rotation Control", self.show_control_panel, "#5D4037"),
            ("🔄 Apply Now", self.apply_ua, "#689F38")
        ]
        
        for text, cmd, color in buttons:
            ctk.CTkButton(
                btn_panel,
                text=text,
                command=cmd,
                fg_color=color,
                hover_color=self.darken_color(color),
                width=140,
                height=40
            ).pack(side="left", padx=5)
    
    def darken_color(self, hex_color, factor=0.8):
        """Darken a hex color"""
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        darkened = tuple(max(0, int(c * factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def load_user_agents(self):
        """Load all user-agents from directory"""
        self.user_agents = []
        if not os.path.exists(self.ua_dir):
            os.makedirs(self.ua_dir)
        
        for file in os.listdir(self.ua_dir):
            if file.endswith(".txt"):
                try:
                    with open(os.path.join(self.ua_dir, file), 'r') as f:
                        ua = f.read().strip()
                        if ua:
                            self.user_agents.append(ua)
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")
    
    def refresh_ua_list(self):
        """Update the UA list display"""
        self.ua_list.configure(state="normal")
        self.ua_list.delete("1.0", "end")
        
        if not self.user_agents:
            self.ua_list.insert("end", "No user-agents found. Import or add some!")
        else:
            for i, ua in enumerate(self.user_agents, 1):
                self.ua_list.insert("end", f"{i}. {ua}\n")
        
        self.ua_list.configure(state="disabled")
    
    def update_ua_display(self):
        """Update current UA display"""
        self.ua_display.configure(state="normal")
        self.ua_display.delete("1.0", "end")
        
        if self.current_ua:
            status = "ACTIVE" if self.rotation_active else "READY"
            color = "green" if self.rotation_active else "yellow"
            self.ua_display.tag_config("status", foreground=color)
            
            self.ua_display.insert("end", f"🛡️ Current User-Agent ({status}):\n", "status")
            self.ua_display.insert("end", f"{self.current_ua}\n\n")
            
            if self.rotation_active:
                self.ua_display.insert("end", f"⏱ Next rotation in: {self.rotation_interval} seconds\n")
        else:
            self.ua_display.insert("end", "⚠️ No User-Agent currently set\n")
        
        self.ua_display.configure(state="disabled")
    
    def import_ua(self):
        """Import UAs from file"""
        file = filedialog.askopenfilename(title="Select UA File", filetypes=[("Text files", "*.txt")])
        if not file:
            return
        
        try:
            with open(file, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
                # Validate format
                valid = all(
                    "Mozilla/5.0" in line and ("Firefox" in line or "Chrome" in line)
                    for line in lines
                )
                
                if not valid:
                    messagebox.showerror("Invalid Format", "File contains invalid User-Agent strings!")
                    return
                
                # Save each UA
                for i, ua in enumerate(lines):
                    filename = f"ua_{int(time.time())}_{i}.txt"
                    with open(os.path.join(self.ua_dir, filename), 'w') as uaf:
                        uaf.write(ua)
                
                self.load_user_agents()
                self.refresh_ua_list()
                messagebox.showinfo("Success", f"Imported {len(lines)} User-Agent(s)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {str(e)}")
    
    def add_manual_ua(self):
        """Add UA manually via dialog"""
        dialog = ctk.CTkInputDialog(
            text="Enter User-Agent string:",
            title="Add User-Agent"
        )
        
        ua = dialog.get_input()
        if not ua:
            return
        
        # Validate
        if not ("Mozilla/5.0" in ua and ("Firefox" in ua or "Chrome" in ua)):
            messagebox.showerror("Invalid", "Not a valid User-Agent string!")
            return
        
        # Save to file
        filename = f"manual_{int(time.time())}.txt"
        try:
            with open(os.path.join(self.ua_dir, filename), 'w') as f:
                f.write(ua)
            
            self.load_user_agents()
            self.refresh_ua_list()
            messagebox.showinfo("Success", "User-Agent added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add: {str(e)}")
    
    def delete_ua(self):
        """Delete selected UA"""
        if not self.user_agents:
            messagebox.showwarning("Warning", "No User-Agents to delete")
            return
        
        try:
            # Get selected line
            index = self.ua_list.index("insert linestart")
            line = self.ua_list.get(index, index + " lineend").strip()
            
            if not line or not line[0].isdigit():
                messagebox.showwarning("Warning", "Please select a User-Agent to delete")
                return
            
            ua_index = int(line.split(".")[0]) - 1
            if 0 <= ua_index < len(self.user_agents):
                target_ua = self.user_agents[ua_index]
                
                # Find and delete corresponding file
                for file in os.listdir(self.ua_dir):
                    try:
                        with open(os.path.join(self.ua_dir, file), 'r') as f:
                            if f.read().strip() == target_ua:
                                os.remove(os.path.join(self.ua_dir, file))
                                break
                    except:
                        continue
                
                self.load_user_agents()
                self.refresh_ua_list()
                messagebox.showinfo("Success", "User-Agent deleted!")
            else:
                messagebox.showwarning("Warning", "Invalid selection")
                
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {str(e)}")
    
    def show_control_panel(self):
        """Show rotation control panel"""
        panel = ctk.CTkToplevel(self.root)
        panel.title("⚙️ Rotation Control")
        panel.geometry("500x400")
        
        if self.lock_gui:
            panel.resizable(False, False)
            panel.grab_set()
        
        # Current UA frame
        current_frame = ctk.CTkFrame(panel)
        current_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(current_frame, 
                    text="Current User-Agent:",
                    font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.current_label = ctk.CTkLabel(
            current_frame,
            text=self.current_ua or "None",
            wraplength=450,
            justify="left"
        )
        self.current_label.pack(fill="x", pady=5)
        
        # Rotation control
        control_frame = ctk.CTkFrame(panel)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(control_frame, 
                    text="Rotation Interval (seconds):",
                    font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        
        self.interval_entry = ctk.CTkEntry(control_frame, width=100)
        self.interval_entry.grid(row=0, column=1, padx=5)
        self.interval_entry.insert(0, str(self.rotation_interval))
        
        # Rotation button
        self.rotate_btn = ctk.CTkButton(
            control_frame,
            text="START ROTATION" if not self.rotation_active else "STOP ROTATION",
            command=self.toggle_rotation,
            fg_color="#4CAF50" if not self.rotation_active else "#F44336",
            hover_color="#388E3C" if not self.rotation_active else "#D32F2F",
            width=150
        )
        self.rotate_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # System options
        sys_frame = ctk.CTkFrame(panel)
        sys_frame.pack(fill="x", padx=10, pady=10)
        
        self.lock_var = ctk.BooleanVar(value=self.lock_gui)
        ctk.CTkCheckBox(
            sys_frame,
            text="🔒 Lock GUI (prevent closing)",
            variable=self.lock_var,
            command=self.toggle_gui_lock
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            sys_frame,
            text="🛠️ System Info",
            command=self.show_system_info,
            width=120
        ).pack(side="right", padx=5)
    
    def toggle_rotation(self):
        """Toggle rotation on/off"""
        if not self.user_agents:
            messagebox.showwarning("Warning", "No User-Agents available!")
            return
        
        try:
            self.rotation_interval = max(5, int(self.interval_entry.get()))
        except:
            messagebox.showerror("Error", "Invalid interval value")
            return
        
        self.rotation_active = not self.rotation_active
        
        if self.rotation_active:
            self.rotate_btn.configure(
                text="STOP ROTATION",
                fg_color="#F44336",
                hover_color="#D32F2F"
            )
            self.start_rotation()
        else:
            self.rotate_btn.configure(
                text="START ROTATION",
                fg_color="#4CAF50",
                hover_color="#388E3C"
            )
            self.stop_rotation()
        
        self.update_ua_display()
    
    def start_rotation(self):
        """Start the rotation thread"""
        if not hasattr(self, 'rotation_thread') or not self.rotation_thread.is_alive():
            self.rotation_thread = threading.Thread(
                target=self.rotation_worker,
                daemon=True
            )
            self.rotation_thread.start()
    
    def stop_rotation(self):
        """Stop the rotation"""
        self.rotation_active = False
    
    def rotation_worker(self):
        """Worker thread for rotation"""
        while self.rotation_active:
            self.apply_ua()
            
            # Countdown with check for stop
            for _ in range(self.rotation_interval * 10):
                if not self.rotation_active:
                    return
                time.sleep(0.1)
    
    def apply_ua(self):
        """Apply a new random User-Agent"""
        if not self.user_agents:
            return
        
        new_ua = random.choice(self.user_agents)
        self.current_ua = new_ua
        
        # Save current UA to temp file
        with open(self.temp_ua_file, 'w') as f:
            f.write(new_ua)
        
        # Apply system-wide (Linux-specific)
        try:
            # Method 1: Environment variable
            os.environ['HTTP_USER_AGENT'] = new_ua
            
            # Method 2: Proxychains configuration
            if os.path.exists(self.proxy_config_file):
                with open(self.proxy_config_file, 'a') as f:
                    f.write(f"\n# User-Agent rotation\nheader add User-Agent \"{new_ua}\"\n")
            
            # Method 3: Firefox profile (if exists)
            firefox_profile = os.path.expanduser("~/.mozilla/firefox")
            if os.path.exists(firefox_profile):
                for profile in os.listdir(firefox_profile):
                    if profile.endswith('.default-release'):
                        prefs_file = os.path.join(firefox_profile, profile, 'user.js')
                        with open(prefs_file, 'a') as f:
                            f.write(f'\nuser_pref("general.useragent.override", "{new_ua}");\n')
            
            # Update display
            self.update_ua_display()
            if hasattr(self, 'current_label'):
                self.current_label.configure(text=new_ua)
            
            print(f"[SYSTEM] Applied User-Agent: {new_ua}")
            
        except Exception as e:
            print(f"[ERROR] Failed to apply UA: {str(e)}")
    
    def toggle_gui_lock(self):
        """Toggle GUI lock state"""
        self.lock_gui = self.lock_var.get()
        
        if self.lock_gui:
            self.root.resizable(False, False)
            self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        else:
            self.root.resizable(True, True)
            self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
    
    def show_system_info(self):
        """Show system information"""
        info = f"""
        System User-Agent Status:
        -------------------------
        Current UA: {self.current_ua or "None"}
        Rotation: {'ACTIVE' if self.rotation_active else 'INACTIVE'}
        Interval: {self.rotation_interval} seconds
        Total UAs: {len(self.user_agents)}
        
        Applied Methods:
        - Environment Variables
        - Proxychains Config
        - Firefox Profile
        """
        
        messagebox.showinfo("System Info", info.strip())
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RealUserAgentRotator()
    app.run()
