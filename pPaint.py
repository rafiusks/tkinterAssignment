import tkinter as tk
from tkinter import colorchooser

# Default color is black
current_color = "#000000"

# Function to change the color using the color picker
def choose_color(event=None):
    global current_color
    color = colorchooser.askcolor(title="Pick a color")
    if color[1] is not None:  # Check if a color is selected
        current_color = color[1]
        color_display.config(bg=current_color)  # Update the color display
        hex_input.delete(0, tk.END)  # Clear the hex input field
        hex_input.insert(0, current_color)  # Insert the new hex value

# Function to update the color based on manual hex input
def update_color_from_hex(event=None):
    global current_color
    new_color = hex_input.get()
    if len(new_color) == 7 and new_color[0] == '#':  # Validate hex format (# followed by 6 characters)
        try:
            color_display.config(bg=new_color)  # Update the color display
            current_color = new_color  # Update the current color
        except tk.TclError:
            pass  # Ignore invalid colors

# Function to draw on the canvas
def paint(event):
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    canvas.create_line(x1, y1, x2, y2, fill=current_color, width=3)

# Create the main window
root = tk.Tk()
root.title("Simple Drawing Application")
root.geometry("800x600")

# Create a frame for the color display and input
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP)

# Add a color display box, which will trigger the color picker on click
color_display = tk.Label(top_frame, bg=current_color, width=10, height=2)
color_display.pack(side=tk.LEFT, padx=10, pady=10)

# Bind the color display box to the color picker function (left-click to trigger)
color_display.bind("<Button-1>", choose_color)

# Add a hex input field for the color
hex_input = tk.Entry(top_frame, width=10)
hex_input.insert(0, current_color)  # Initialize the input with the current color
hex_input.pack(side=tk.LEFT, padx=10)
hex_input.bind("<Return>", update_color_from_hex)  # Update color on Enter key press

# Create a canvas widget below the color picker and display box
canvas = tk.Canvas(root, bg="white", width=800, height=600)
canvas.pack(fill=tk.BOTH, expand=True)

# Bind mouse movement to the paint function
canvas.bind("<B1-Motion>", paint)

# Start the Tkinter main loop
root.mainloop()