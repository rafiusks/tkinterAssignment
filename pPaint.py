import tkinter as tk
from tkinter import colorchooser

# Default settings
current_color = "#000000"
current_tool = "brush"  # Default tool is brush

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
    if len(new_color) == 7 and new_color[0] == '#':  # Validate hex format
        try:
            color_display.config(bg=new_color)  # Update the color display
            current_color = new_color  # Update the current color
        except tk.TclError:
            pass  # Ignore invalid colors

# Function to select the drawing tool
def select_tool(tool):
    global current_tool
    current_tool = tool

# Function to start drawing shapes or freehand
start_x, start_y = None, None
def start_draw(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y

# Function to draw on the canvas based on the selected tool
def paint(event):
    global start_x, start_y
    if current_tool == "brush":
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        canvas.create_line(x1, y1, x2, y2, fill=current_color, width=3)
    elif current_tool == "rectangle":
        canvas.delete("preview")
        canvas.create_rectangle(start_x, start_y, event.x, event.y, outline=current_color, tags="preview")
    elif current_tool == "circle":
        canvas.delete("preview")
        canvas.create_oval(start_x, start_y, event.x, event.y, outline=current_color, tags="preview")
    elif current_tool == "line":
        canvas.delete("preview")
        canvas.create_line(start_x, start_y, event.x, event.y, fill=current_color, tags="preview")

# Function to finalize shape drawing (when mouse button is released)
def finalize_shape(event):
    if current_tool == "rectangle":
        canvas.create_rectangle(start_x, start_y, event.x, event.y, outline=current_color)
    elif current_tool == "circle":
        canvas.create_oval(start_x, start_y, event.x, event.y, outline=current_color)
    elif current_tool == "line":
        canvas.create_line(start_x, start_y, event.x, event.y, fill=current_color)
    canvas.delete("preview")  # Clear the preview shape

# Create the main window
root = tk.Tk()
root.title("Simple Drawing Application")
root.geometry("900x600")

# Create a frame for the toolbar (top section)
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X)

# Add color display box (clickable) and hex input
color_display = tk.Label(top_frame, bg=current_color, width=10, height=2)
color_display.pack(side=tk.LEFT, padx=10, pady=10)
color_display.bind("<Button-1>", choose_color)

hex_input = tk.Entry(top_frame, width=10)
hex_input.insert(0, current_color)  # Initialize with current color
hex_input.pack(side=tk.LEFT, padx=10)
hex_input.bind("<Return>", update_color_from_hex)

# Add buttons for shape tools
tools_frame = tk.Frame(top_frame)
tools_frame.pack(side=tk.LEFT, padx=10)

brush_button = tk.Button(tools_frame, text="Brush", command=lambda: select_tool("brush"))
brush_button.pack(side=tk.LEFT)

rectangle_button = tk.Button(tools_frame, text="Rectangle", command=lambda: select_tool("rectangle"))
rectangle_button.pack(side=tk.LEFT)

circle_button = tk.Button(tools_frame, text="Circle", command=lambda: select_tool("circle"))
circle_button.pack(side=tk.LEFT)

line_button = tk.Button(tools_frame, text="Line", command=lambda: select_tool("line"))
line_button.pack(side=tk.LEFT)

# Create the canvas for drawing
canvas = tk.Canvas(root, bg="white", width=800, height=500)
canvas.pack(fill=tk.BOTH, expand=True)

# Bind mouse events to the canvas for drawing and shape creation
canvas.bind("<B1-Motion>", paint)  # Mouse movement for freehand drawing or shape preview
canvas.bind("<ButtonPress-1>", start_draw)  # Start drawing when mouse is pressed
canvas.bind("<ButtonRelease-1>", finalize_shape)  # Finalize shape when mouse is released

# Start the Tkinter main loop
root.mainloop()