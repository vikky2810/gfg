import tkinter as tk
from tkinter import ttk, messagebox
import os
import math
import threading
from queue import Queue
import time
import string
from ctypes import windll
import shutil

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")
        
        # Remove default title bar
        self.root.overrideredirect(True)
        
        # Queue for communication between threads
        self.size_queue = Queue()
        
        # Custom title bar
        self.create_title_bar()
        
        # Path display
        self.path_var = tk.StringVar()
        self.create_path_display()
        
        # Navigation buttons
        self.create_navigation_buttons()
        
        # Create Treeview
        self.create_treeview()
        
        # Initialize with My Computer view
        self.show_my_computer()

    def create_title_bar(self):
        title_bar = tk.Frame(self.root, bg="#1f1f1f", relief="raised", bd=0)
        title_bar.pack(fill="x")
        
        # Title
        title_label = tk.Label(title_bar, text="File Manager", bg="#1f1f1f", fg="white", pady=5)
        title_label.pack(side="left", padx=10)
        
        # Close button
        close_button = tk.Button(title_bar, text="×", bg="#1f1f1f", fg="white",
                               bd=0, padx=10, command=self.root.destroy)
        close_button.pack(side="right")
        
        # Bind dragging functionality
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.on_move)

    def create_path_display(self):
        path_frame = tk.Frame(self.root, bg="#2b2b2b")
        path_frame.pack(fill="x", padx=10, pady=5)
        
        path_label = tk.Label(path_frame, textvariable=self.path_var,
                            bg="#2b2b2b", fg="white", anchor="w")
        path_label.pack(fill="x")

    def create_navigation_buttons(self):
        nav_frame = tk.Frame(self.root, bg="#2b2b2b")
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        # My Computer button
        my_computer_button = tk.Button(nav_frame, text="My Computer", command=self.show_my_computer,
                                     bg="#3c3f41", fg="white", bd=0)
        my_computer_button.pack(side="left", padx=(0, 5))
        
        # Up button
        up_button = tk.Button(nav_frame, text="↑ Up", command=self.go_up,
                            bg="#3c3f41", fg="white", bd=0)
        up_button.pack(side="left")

    def create_treeview(self):
        # Create Treeview with custom style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading",
                       background="#1f1f1f",
                       foreground="white")
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(self.root)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview
        self.tree = ttk.Treeview(self.root, columns=("size",),
                                show="tree headings",
                                yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading("size", text="Size")
        self.tree.column("size", width=100)
        
        # Configure tags for folders and files
        self.tree.tag_configure('folder', foreground='#87CEEB')  # Light blue for folders
        self.tree.tag_configure('file', foreground='white')      # White for files
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def format_size(self, size):
        if size is None:
            return "Calculating..."
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_folder_size(self, folder):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        except (PermissionError, OSError):
            return 0
        return total_size

    def calculate_folder_size_async(self, folder, item_id):
        """Calculate folder size in a separate thread"""
        size = self.get_folder_size(folder)
        self.size_queue.put((item_id, size))
        
    def update_sizes(self):
        """Update folder sizes as they become available"""
        try:
            while True:
                item_id, size = self.size_queue.get_nowait()
                self.tree.set(item_id, "size", self.format_size(size))
        except:
            # Queue is empty, schedule next check
            self.root.after(100, self.update_sizes)

    def display_files(self, path):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # List all items first
            items = os.listdir(path)
            
            # Separate directories and files
            dirs = []
            files = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)
            
            # Display directories first
            for item in sorted(dirs):
                full_path = os.path.join(path, item)
                try:
                    # Insert directory with temporary size
                    item_id = self.tree.insert("", "end", text=item,
                                             values=("Calculating...",),
                                             tags=('folder',))  # Add folder tag
                    # Start size calculation in background
                    thread = threading.Thread(
                        target=self.calculate_folder_size_async,
                        args=(full_path, item_id)
                    )
                    thread.daemon = True
                    thread.start()
                except (PermissionError, OSError):
                    continue
            
            # Then display files
            for item in sorted(files):
                full_path = os.path.join(path, item)
                try:
                    size = os.path.getsize(full_path)
                    self.tree.insert("", "end", text=item,
                                   values=(self.format_size(size),),
                                   tags=('file',))  # Add file tag
                except (PermissionError, OSError):
                    continue
                    
        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
        
        # Start updating sizes
        self.root.after(100, self.update_sizes)

    def update_path(self, path):
        self.current_path = path
        self.path_var.set(path)
        self.display_files(path)

    def go_up(self):
        # If we're already at My Computer view, do nothing
        if self.current_path is None:
            return
            
        # If we're at a root directory, go to My Computer view
        if os.name == 'nt' and len(self.current_path) <= 3:
            self.show_my_computer()
            return
            
        # Normal directory up navigation
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.update_path(parent)

    def on_item_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_text = self.tree.item(item)["text"]
        
        # Handle drive selection from My Computer view
        if self.current_path is None:  # We're in My Computer view
            drive = item_text.split()[0]  # Get drive letter (e.g., "C:\")
            self.update_path(drive)
            return
            
        # Normal folder navigation
        new_path = os.path.join(self.current_path, item_text)
        if os.path.isdir(new_path):
            self.update_path(new_path)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def get_available_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive_path = f"{letter}:\\"
                try:
                    drive_type = windll.kernel32.GetDriveTypeW(drive_path)
                    # 3 is DRIVE_FIXED (hard drive)
                    # 2 is DRIVE_REMOVABLE (USB, etc.)
                    if drive_type in [2, 3]:
                        drives.append(drive_path)
                except:
                    pass
            bitmask >>= 1
        return drives

    def show_my_computer(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Set path to "My Computer"
        self.path_var.set("My Computer")
        self.current_path = None
        
        # Get and display available drives
        drives = self.get_available_drives()
        for drive in drives:
            try:
                total, used, free = self.get_drive_space(drive)
                drive_text = f"{drive} (Free: {self.format_size(free)} / Total: {self.format_size(total)})"
                self.tree.insert("", "end", text=drive_text,
                               values=("Drive",),
                               tags=('folder',))
            except:
                self.tree.insert("", "end", text=drive,
                               values=("Drive",),
                               tags=('folder',))

    def get_drive_space(self, drive):
        total, used, free = (0, 0, 0)
        try:
            total, used, free, = shutil.disk_usage(drive)
        except:
            pass
        return total, used, free

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop() 