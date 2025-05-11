# File Manager

A modern, dark-themed file manager built with Python and Tkinter. This application provides an intuitive interface for navigating your file system and viewing file/folder sizes.

## Features

- Dark theme interface for reduced eye strain
- File and folder size calculation
- Hierarchical directory navigation
- Custom title bar with window dragging
- File size display in human-readable format
- Directory size calculation (recursive)
- Error handling for permission issues
- Sortable file/folder list

## Requirements

- Python 3.x
- tkinter (usually comes with Python)

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