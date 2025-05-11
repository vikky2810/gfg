import tkinter as tk
from tkinter import ttk, messagebox
import os
import math
import threading
from queue import Queue
import time
import string
from ctypes import windll
import ctypes
import shutil
from datetime import datetime
import mimetypes
from tkinter import filedialog

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2b2b2b")
        
        # Remove default title bar
        self.root.overrideredirect(True)
        
        # Queue for communication between threads
        self.size_queue = Queue()
        
        # Sorting variables
        self.sort_by = "name"
        self.sort_reverse = False
        
        # Filter variables
        self.file_type_filter = "All"
        self.size_min = 0
        self.size_max = float('inf')
        self.date_min = None
        self.date_max = None
        self.date_range = None  # Initialize date_range
        
        # Custom title bar
        self.create_title_bar()
        
        # Path display
        self.path_var = tk.StringVar()
        self.create_path_display()
        
        # Create main content frame
        self.content_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.content_frame.pack(fill="both", expand=True)
        
        # Create filter panel
        self.create_filter_panel()
        
        # Create file view frame
        self.file_view_frame = tk.Frame(self.content_frame, bg="#2b2b2b")
        self.file_view_frame.pack(side="right", fill="both", expand=True)
        
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

    def create_filter_panel(self):
        filter_frame = tk.Frame(self.content_frame, bg="#1f1f1f", width=200)
        filter_frame.pack(side="left", fill="y", padx=5, pady=5)
        filter_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Title
        title = tk.Label(filter_frame, text="Filters", bg="#1f1f1f", fg="white", font=("Arial", 12, "bold"))
        title.pack(pady=10)
        
        # File Type Filter
        type_frame = tk.LabelFrame(filter_frame, text="File Type", bg="#1f1f1f", fg="white")
        type_frame.pack(fill="x", padx=5, pady=5)
        
        self.type_var = tk.StringVar(value="All")
        types = ["All", "Documents", "Images", "Audio", "Video", "Archives", "Others"]
        for t in types:
            tk.Radiobutton(type_frame, text=t, value=t, variable=self.type_var,
                          bg="#1f1f1f", fg="white", selectcolor="#3c3f41",
                          command=self.apply_filters).pack(anchor="w")
        
        # Size Filter
        size_frame = tk.LabelFrame(filter_frame, text="Size Range", bg="#1f1f1f", fg="white")
        size_frame.pack(fill="x", padx=5, pady=5)
        
        sizes = ["Any", "<10MB", "10MB-100MB", "100MB-1GB", ">1GB"]
        self.size_var = tk.StringVar(value="Any")
        for s in sizes:
            tk.Radiobutton(size_frame, text=s, value=s, variable=self.size_var,
                          bg="#1f1f1f", fg="white", selectcolor="#3c3f41",
                          command=self.apply_filters).pack(anchor="w")
        
        # Date Filter
        date_frame = tk.LabelFrame(filter_frame, text="Date Modified", bg="#1f1f1f", fg="white")
        date_frame.pack(fill="x", padx=5, pady=5)
        
        dates = ["Any time", "Today", "This week", "This month", "This year"]
        self.date_var = tk.StringVar(value="Any time")
        for d in dates:
            tk.Radiobutton(date_frame, text=d, value=d, variable=self.date_var,
                          bg="#1f1f1f", fg="white", selectcolor="#3c3f41",
                          command=self.apply_filters).pack(anchor="w")
        
        # Reset Filters Button
        reset_btn = tk.Button(filter_frame, text="Reset Filters", command=self.reset_filters,
                            bg="#3c3f41", fg="white", bd=0)
        reset_btn.pack(pady=10)

    def apply_filters(self):
        if self.current_path is None:
            return
            
        # Get filter values
        type_filter = self.type_var.get()
        size_filter = self.size_var.get()
        date_filter = self.date_var.get()
        
        # Process size filter
        size_ranges = {
            "Any": (0, float('inf')),
            "<10MB": (0, 10 * 1024 * 1024),
            "10MB-100MB": (10 * 1024 * 1024, 100 * 1024 * 1024),
            "100MB-1GB": (100 * 1024 * 1024, 1024 * 1024 * 1024),
            ">1GB": (1024 * 1024 * 1024, float('inf'))
        }
        self.size_min, self.size_max = size_ranges[size_filter]
        
        # Process date filter
        now = datetime.now()
        date_ranges = {
            "Any time": None,
            "Today": (now.replace(hour=0, minute=0, second=0), now),
            "This week": (now.replace(day=now.day-now.weekday(), hour=0, minute=0, second=0), now),
            "This month": (now.replace(day=1, hour=0, minute=0, second=0), now),
            "This year": (now.replace(month=1, day=1, hour=0, minute=0, second=0), now)
        }
        self.date_range = date_ranges[date_filter]
        
        # Update display
        self.display_files(self.current_path)

    def reset_filters(self):
        self.type_var.set("All")
        self.size_var.set("Any")
        self.date_var.set("Any time")
        self.apply_filters()

    def get_file_type_category(self, file_path):
        if os.path.isdir(file_path):
            return "Folder"
            
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            return "Others"
            
        if mime_type.startswith('text/') or mime_type in ['application/pdf', 'application/msword']:
            return "Documents"
        elif mime_type.startswith('image/'):
            return "Images"
        elif mime_type.startswith('audio/'):
            return "Audio"
        elif mime_type.startswith('video/'):
            return "Video"
        elif mime_type in ['application/zip', 'application/x-rar-compressed']:
            return "Archives"
        else:
            return "Others"

    def should_show_item(self, full_path, file_type, size, mtime):
        try:
            # Always show folders
            if os.path.isdir(full_path):
                return True
                
            # Check file type filter
            if self.type_var.get() != "All":
                if self.get_file_type_category(full_path) != self.type_var.get():
                    return False
            
            # Check size filter (only for files)
            if not os.path.isdir(full_path):  # Only apply size filter to files
                if not (self.size_min <= size <= self.size_max):
                    return False
            
            # Check date filter
            if hasattr(self, 'date_range') and self.date_range:
                start_date, end_date = self.date_range
                mtime_dt = datetime.fromtimestamp(mtime)
                if not (start_date <= mtime_dt <= end_date):
                    return False
            
            return True
        except Exception as e:
            print(f"Error in should_show_item: {str(e)}")
            return True  # Show item by default if there's an error

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
        scrollbar = ttk.Scrollbar(self.file_view_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview with multiple columns
        self.tree = ttk.Treeview(self.file_view_frame,
                                columns=("name", "size", "type", "modified"),
                                show="headings",
                                yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading("name", text="Name", command=lambda: self.sort_items("name"))
        self.tree.heading("size", text="Size", command=lambda: self.sort_items("size"))
        self.tree.heading("type", text="Type", command=lambda: self.sort_items("type"))
        self.tree.heading("modified", text="Modified", command=lambda: self.sort_items("modified"))
        
        # Set column widths
        self.tree.column("name", width=300)
        self.tree.column("size", width=100)
        self.tree.column("type", width=100)
        self.tree.column("modified", width=150)
        
        # Configure tags for folders and files
        self.tree.tag_configure('folder', foreground='#87CEEB')
        self.tree.tag_configure('file', foreground='white')
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def sort_items(self, column):
        if self.current_path is None:
            return
            
        if self.sort_by == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = column
            self.sort_reverse = False
            
        self.display_files(self.current_path)

    def format_size(self, size):
        if size is None:
            return "Calculating..."
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_folder_size(self, folder):
        """Calculate the total size of a folder"""
        if not os.path.exists(folder):
            return 0
            
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder, onerror=None):
                for f in filenames:
                    try:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):  # Skip symbolic links
                            total_size += os.path.getsize(fp)
                    except (OSError, FileNotFoundError, PermissionError):
                        continue
        except (OSError, PermissionError):
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
            # Get all items with their information
            items = []
            for item in os.listdir(path):
                try:
                    full_path = os.path.join(path, item)
                    stats = os.stat(full_path)
                    
                    # Get size based on whether it's a file or directory
                    try:
                        if os.path.isfile(full_path):
                            size = stats.st_size
                        else:
                            # For directories, show "Folder" instead of size initially
                            size = 0
                    except:
                        size = 0
                    
                    mtime = stats.st_mtime
                    
                    if self.should_show_item(full_path, self.get_file_type_category(full_path), size, mtime):
                        items.append({
                            'name': item,
                            'path': full_path,
                            'size': size,
                            'type': self.get_file_type_category(full_path),
                            'modified': mtime,
                            'is_dir': os.path.isdir(full_path)
                        })
                except (PermissionError, OSError) as e:
                    print(f"Error accessing {item}: {str(e)}")
                    continue
            
            # Sort items
            items.sort(key=lambda x: (
                not x['is_dir'],  # Directories first
                {
                    'name': x['name'].lower(),
                    'size': x['size'],
                    'type': x['type'],
                    'modified': x['modified']
                }[self.sort_by]
            ), reverse=self.sort_reverse)
            
            # Display items
            for item in items:
                try:
                    if item['is_dir']:
                        # For directories, start a thread to calculate size
                        item_id = self.tree.insert("", "end",
                                                 values=(
                                                     item['name'],
                                                     "Calculating...",
                                                     item['type'],
                                                     datetime.fromtimestamp(item['modified']).strftime('%Y-%m-%d %H:%M')
                                                 ),
                                                 tags=('folder',))
                        # Start size calculation in background
                        thread = threading.Thread(
                            target=self.calculate_folder_size_async,
                            args=(item['path'], item_id)
                        )
                        thread.daemon = True
                        thread.start()
                    else:
                        self.tree.insert("", "end",
                                       values=(
                                           item['name'],
                                           self.format_size(item['size']),
                                           item['type'],
                                           datetime.fromtimestamp(item['modified']).strftime('%Y-%m-%d %H:%M')
                                       ),
                                       tags=('file',))
                except Exception as e:
                    print(f"Error displaying {item['name']}: {str(e)}")
                    continue
                    
        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
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
        item_values = self.tree.item(item)["values"]
        if not item_values:
            return
            
        item_name = item_values[0]  # Name is now the first column
        
        # Handle drive selection from My Computer view
        if self.current_path is None:  # We're in My Computer view
            # Extract drive letter from the text (e.g., "Local Disk (C:)" -> "C:")
            drive = item_name.split("(")[1].split(")")[0] + "\\"
            self.update_path(drive)
            return
            
        # Normal folder navigation
        new_path = os.path.join(self.current_path, item_name)
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
                    # Include all drive types except DRIVE_NO_ROOT_DIR (1)
                    if drive_type > 1:
                        drives.append(drive_path)
                except:
                    pass
            bitmask >>= 1
        return drives

    def get_drive_space(self, drive):
        try:
            usage = shutil.disk_usage(drive)
            return usage.total, usage.used, usage.free
        except:
            return 0, 0, 0

    def show_my_computer(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Set path to "My Computer"
        self.path_var.set("My Computer")
        self.current_path = None
        
        try:
            # Get and display available drives
            drives = self.get_available_drives()
            for drive in sorted(drives):
                try:
                    # Get drive type
                    drive_type = windll.kernel32.GetDriveTypeW(drive)
                    
                    # Get volume name
                    volume_name_buffer = ctypes.create_unicode_buffer(1024)
                    file_system_name_buffer = ctypes.create_unicode_buffer(1024)
                    windll.kernel32.GetVolumeInformationW(
                        drive,
                        volume_name_buffer,
                        ctypes.sizeof(volume_name_buffer),
                        None, None, None,
                        file_system_name_buffer,
                        ctypes.sizeof(file_system_name_buffer)
                    )
                    volume_name = volume_name_buffer.value
                    
                    # Set drive label based on type
                    if drive_type == 2:  # DRIVE_REMOVABLE
                        drive_label = "Removable Drive"
                    elif drive_type == 3:  # DRIVE_FIXED
                        drive_label = "Local Disk"
                    elif drive_type == 4:  # DRIVE_REMOTE
                        drive_label = "Network Drive"
                    elif drive_type == 5:  # DRIVE_CDROM
                        drive_label = "CD/DVD Drive"
                    else:
                        drive_label = "Drive"
                    
                    # Get drive space
                    total, used, free = self.get_drive_space(drive)
                    
                    # Format drive text
                    drive_letter = drive[0]
                    if volume_name:
                        drive_name = f"{volume_name} ({drive_letter}:)"
                    else:
                        drive_name = f"{drive_label} ({drive_letter}:)"
                    
                    # Add size information
                    size_info = f"Free: {self.format_size(free)} / Total: {self.format_size(total)}" if total > 0 else "Unknown"
                    
                    self.tree.insert("", "end",
                                   values=(
                                       drive_name,
                                       size_info,
                                       drive_label,
                                       datetime.fromtimestamp(os.path.getctime(drive)).strftime('%Y-%m-%d %H:%M')
                                   ),
                                   tags=('folder',))
                except Exception as e:
                    print(f"Error displaying drive {drive}: {str(e)}")
                    # Fallback for any errors
                    drive_letter = drive[0]
                    self.tree.insert("", "end",
                                   values=(
                                       f"Local Disk ({drive_letter}:)",
                                       "Unknown",
                                       "Drive",
                                       ""
                                   ),
                                   tags=('folder',))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop() 