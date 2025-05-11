# Modern File Manager

A modern, feature-rich file management application built with Python and Tkinter, featuring a dark theme and intuitive user interface.

## Features

### Core Functionality
- Browse and navigate through files and folders
- Display file properties (name, size, type, modification date)
- Calculate folder sizes asynchronously
- Support for all drive types (Local, Removable, Network, CD/DVD)
- "My Computer" view showing all available drives with space information

### User Interface
- Modern dark theme with custom styling
- Custom title bar with window dragging support
- Breadcrumb navigation for easy directory traversal
- Status bar showing selected and total items information
- Tooltips for buttons, items, and column headers
- Responsive design with proper error handling

### Navigation
- Up button to go to parent directory
- Back and Forward navigation
- Refresh button to update current view
- Double-click to open folders
- Breadcrumb buttons for quick navigation to any parent folder

### File Display
- Hierarchical view of files and folders
- Color-coded items (folders in light blue, files in white)
- Sortable columns (Name, Size, Type, Modified)
- Asynchronous folder size calculation
- File type categorization

### Filtering System
- Filter by file type:
  - All
  - Documents
  - Images
  - Audio
  - Video
  - Archives
  - Others

- Filter by size:
  - Any
  - <10MB
  - 10MB-100MB
  - 100MB-1GB
  - >1GB

- Filter by date modified:
  - Any time
  - Today
  - This week
  - This month
  - This year

### Keyboard Shortcuts
- Alt + Up: Go to parent directory
- Alt + Left: Go back
- Alt + Right: Go forward
- F5: Refresh current view
- Ctrl + A: Select all items
- Ctrl + M: Go to My Computer view

### Information Display
- Detailed file/folder information in tooltips
- Drive information (total space, free space)
- Status bar showing:
  - Number of selected items
  - Total size of selected items
  - Total number of items in current view
  - Total size of items in current view

### Error Handling
- Graceful handling of permission errors
- Safe handling of inaccessible files and folders
- Fallback behavior for drive information
- Background processing for large operations

## Technical Features
- Asynchronous folder size calculation using threads
- Queue-based communication between threads
- Custom event handling for UI interactions
- Efficient file system operations
- Memory-efficient large folder handling
- Type-specific file categorization using MIME types

## Requirements
- Python 3.x
- tkinter (usually comes with Python)
- Windows OS (for drive management features)

## Future Enhancements (Planned)
- File operations (copy, move, delete)
- Search functionality
- Context menus
- Drag and drop support
- Multiple view modes (list, icons, details)
- File preview
- Favorites/Bookmarks
- Archive handling
- Extended file properties

## Installation

1. Clone this repository or download the files
2. Make sure you have Python 3.x installed
3. No additional packages are required as tkinter comes with Python

## Usage

Run the file manager by executing:

```bash
python file_manager.py
```

### Navigation

- Double-click on folders to enter them
- Click the "Up" button to go to the parent directory
- Drag the title bar to move the window
- Click the "×" button to close the application

### Interface

- The current path is displayed at the top
- Files and folders are listed in the main view
- Sizes are shown next to each item
- Folders are listed first, followed by files
- All items are sorted alphabetically

## Features in Detail

### Size Calculation
- File sizes are shown in human-readable format (B, KB, MB, GB, TB)
- Folder sizes are calculated recursively
- Handles permission errors gracefully

### Dark Theme
- Dark gray background (#2b2b2b)
- Light text for contrast
- Custom-styled Treeview widget
- Modern look and feel

### Error Handling
- Gracefully handles permission errors
- Skips inaccessible files and folders
- Shows error messages when needed

## Contributing

Feel free to fork this project and submit pull requests for any improvements you make.

## License

This project is open source and available under the MIT License. 