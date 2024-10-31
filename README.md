# Simple Drawing Application

A user-friendly drawing application built with Python's Tkinter and Pillow (PIL) libraries. This application allows users to create freehand drawings, erase mistakes, draw various shapes, fill areas with color, and manage their color palette efficiently. It also includes undo and redo functionalities to enhance the drawing experience.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Toolbar Tools](#toolbar-tools)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
  - [Menu Options](#menu-options)
- [Dependencies](#dependencies)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Freehand Drawing:** Draw smooth, continuous lines with adjustable brush sizes.
- **Eraser Tool:** Erase parts of your drawing with customizable eraser sizes.
- **Shape Tools:** Draw rectangles, circles, and straight lines with precision.
- **Fill Tool:** Fill enclosed areas with your chosen color using a flood fill algorithm.
- **Color Picker:** Select any color using an intuitive color chooser dialog.
- **Color History:** Access your recently used colors for quick selection.
- **Undo/Redo:** Easily revert or reapply your last actions.
- **Save and Open:** Save your artwork as PNG files and open existing images for editing.
- **Keyboard Shortcuts:** Switch tools and perform actions quickly using keyboard shortcuts.
- **Tooltips:** Get helpful information about tools and features through tooltips.

---

## Installation

### Prerequisites

- **Python 3.7 or higher**: Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **Pillow Library**: Python Imaging Library fork required for image processing.

**Install Dependencies**

   Use `pip` to install the required Python packages.

   ```bash
   pip install Pillow
   ```

   **Note:** Tkinter is included with standard Python installations on Windows and macOS. On some Linux distributions, you may need to install it separately (e.g., `sudo apt-get install python3-tk`).

3. **Run the Application**

   Execute the Python script to start the drawing application.

   ```bash
   python pPaint.py
   ```

---

## Usage

### Toolbar Tools

The application features a toolbar with various tools grouped into categories. Each tool is represented by an icon and has an associated label.

1. **Drawing Tools (Brush and Eraser)**
   - **Brush (🖌️):** Use the brush tool to draw freehand lines.
   - **Eraser (🩹):** Use the eraser to remove parts of your drawing.

2. **Shape Tools (Rectangle, Circle, Line)**
   - **Rectangle (▭):** Draw rectangles by clicking and dragging on the canvas.
   - **Circle (⚪):** Draw circles or ellipses by clicking and dragging.
   - **Line (➖):** Draw straight lines between two points.

3. **Fill Tool**
   - **Fill (🪣):** Fill an enclosed area with the selected color using the fill tool.

4. **Action Tools (Undo and Redo)**
   - **Undo (↩️):** Revert the last action.
   - **Redo (↪️):** Reapply the last undone action.

5. **Color Picker and Brush Size**
   - **Color Picker:** Click the color box to open the color chooser dialog and select a new drawing color.
   - **Brush Size Slider:** Adjust the size of the brush or eraser from 1 to 100.

6. **Color History**
   - Access your last five used colors for quick selection.

### Keyboard Shortcuts

Enhance your productivity by using keyboard shortcuts to switch tools and perform actions:

- **Brush:** `B`
- **Eraser:** `E`
- **Rectangle:** `R`
- **Circle:** `C`
- **Line:** `L`
- **Fill:** `F`
- **Undo:** `Cmd + Z`
- **Redo:** `Shift + Cmd + Z`
- **New File:** `Cmd + N`
- **Open Image:** `Cmd + O`
- **Save Image:** `Cmd + S`
- **Quit Application:** `Cmd + Q`

### Menu Options

The application includes a menu bar with the following options:

1. **File**
   - **New:** Create a new blank drawing. (`Cmd + N`)
   - **Open:** Open an existing image file for editing. (`Cmd + O`)
   - **Save As:** Save your current drawing as a PNG file. (`Cmd + S`)

2. **Edit**
   - **Undo:** Undo the last action. (`Cmd + Z`)
   - **Redo:** Redo the last undone action. (`Shift + Cmd + Z`)

3. **Help**
   - **About:** Display information about the application.
   - **Help:** Display basic instructions for using the application.

---

## Dependencies

- **Python 3.7+**
- **Tkinter:** Standard GUI library for Python.
- **Pillow:** Python Imaging Library for image processing.

Install dependencies using `pip`:

```bash
pip install Pillow
```

**Note:** Tkinter is typically included with Python on Windows and macOS. On some Linux distributions, you may need to install it separately (e.g., `sudo apt-get install python3-tk`).

---

## Acknowledgments

- Built with Python's Tkinter and Pillow libraries.
- Inspired by simple drawing applications available in various operating systems.

---