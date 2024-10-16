import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageDraw, ImageTk

# Default settings
current_color = "#000000"
current_tool = "brush"  # Default tool is brush
brush_size = 3  # Default brush size

# Lists to track actions for undo/redo
actions_stack = []
redo_stack = []

# Create the main window
root = tk.Tk()
root.title("Simple Drawing Application")
root.geometry("900x600")

# Create a frame for the toolbar (top section)
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X)

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

# Function to update brush size from slider
def update_brush_size(value):
    global brush_size
    brush_size = int(value)

# Initialize the drawing surface
canvas_width, canvas_height = 800, 500
image = Image.new("RGBA", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(image)

# Function to update the canvas image
def update_canvas():
    global photo_image
    photo_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=photo_image, anchor=tk.NW)

# Function to start drawing shapes or freehand
start_x, start_y = None, None
def start_draw(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y

    if current_tool in ("rectangle", "circle", "line"):
        # Store the current image for undo
        actions_stack.append(image.copy())
        redo_stack.clear()  # Clear redo stack

# Function to draw on the canvas based on the selected tool
def paint(event):
    global start_x, start_y
    if current_tool == "brush":
        # Draw line on the image
        x1, y1 = event.x - brush_size / 2, event.y - brush_size / 2
        x2, y2 = event.x + brush_size / 2, event.y + brush_size / 2
        draw.ellipse([x1, y1, x2, y2], fill=current_color, outline=current_color)
        update_canvas()
        # For undo functionality
        actions_stack.append(('draw', [x1, y1, x2, y2], current_color))
        redo_stack.clear()  # Clear redo stack
    elif current_tool == "eraser":
        # Erase by drawing white color (or background color)
        x1, y1 = event.x - brush_size / 2, event.y - brush_size / 2
        x2, y2 = event.x + brush_size / 2, event.y + brush_size / 2
        draw.ellipse([x1, y1, x2, y2], fill="white", outline="white")
        update_canvas()
        # For undo functionality
        actions_stack.append(('erase', [x1, y1, x2, y2]))
        redo_stack.clear()  # Clear redo stack
    elif current_tool in ("rectangle", "circle", "line"):
        # Draw a shape preview
        temp_image = image.copy()
        temp_draw = ImageDraw.Draw(temp_image)
        shape_bbox = [start_x, start_y, event.x, event.y]
        if current_tool == "rectangle":
            temp_draw.rectangle(shape_bbox, outline=current_color, width=brush_size)
        elif current_tool == "circle":
            temp_draw.ellipse(shape_bbox, outline=current_color, width=brush_size)
        elif current_tool == "line":
            temp_draw.line([start_x, start_y, event.x, event.y], fill=current_color, width=brush_size)
        # Update canvas with preview
        preview_image = ImageTk.PhotoImage(temp_image)
        canvas.create_image(0, 0, image=preview_image, anchor=tk.NW)
        canvas.image = preview_image  # Keep a reference
    elif current_tool == "fill":
        pass  # Fill tool is handled on mouse release

# Function to finalize shape drawing (when mouse button is released)
def finalize_shape(event):
    global image, draw
    if current_tool in ("rectangle", "circle", "line"):
        shape_bbox = [start_x, start_y, event.x, event.y]
        if current_tool == "rectangle":
            draw.rectangle(shape_bbox, outline=current_color, width=brush_size)
        elif current_tool == "circle":
            draw.ellipse(shape_bbox, outline=current_color, width=brush_size)
        elif current_tool == "line":
            draw.line([start_x, start_y, event.x, event.y], fill=current_color, width=brush_size)
        update_canvas()
    elif current_tool == "fill":
        # Implement fill (bucket tool)
        fill_color = tuple(int(current_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        flood_fill(event.x, event.y, fill_color)
        update_canvas()
    # For undo functionality
    if current_tool in ("rectangle", "circle", "line", "fill"):
        actions_stack.append(image.copy())
        redo_stack.clear()  # Clear redo stack

# Implement flood fill algorithm
def flood_fill(x, y, fill_color):
    target_color = image.getpixel((x, y))
    if target_color == fill_color:
        return

    pixel_data = image.load()
    width, height = image.size
    stack = [(x, y)]

    while stack:
        nx, ny = stack.pop()
        if nx < 0 or nx >= width or ny < 0 or ny >= height:
            continue
        current_color = pixel_data[nx, ny]
        if current_color == target_color:
            pixel_data[nx, ny] = fill_color
            stack.extend([(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)])

# Undo function
def undo():
    if actions_stack:
        last_action = actions_stack.pop()
        if isinstance(last_action, tuple):
            action_type = last_action[0]
            if action_type == 'draw':
                # Erase the last drawing action
                bbox = last_action[1]
                color = last_action[2]
                draw.rectangle(bbox, fill="white", outline="white")
                update_canvas()
                redo_stack.append(last_action)
            elif action_type == 'erase':
                # Re-draw the erased area (not fully accurate without storing previous pixels)
                # For accurate undo, we need to store the pixels before erasing
                pass  # Advanced implementation required
        else:
            # Restore the image state
            redo_stack.append(image.copy())
            image.paste(last_action)
            update_canvas()

# Redo function
def redo():
    if redo_stack:
        next_action = redo_stack.pop()
        if isinstance(next_action, tuple):
            action_type = next_action[0]
            if action_type == 'draw':
                bbox = next_action[1]
                color = next_action[2]
                draw.rectangle(bbox, fill=color, outline=color)
                update_canvas()
                actions_stack.append(next_action)
            elif action_type == 'erase':
                # Re-erase the area
                bbox = next_action[1]
                draw.rectangle(bbox, fill="white", outline="white")
                update_canvas()
                actions_stack.append(next_action)
        else:
            # Restore the image state
            actions_stack.append(image.copy())
            image.paste(next_action)
            update_canvas()

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

eraser_button = tk.Button(tools_frame, text="Eraser", command=lambda: select_tool("eraser"))
eraser_button.pack(side=tk.LEFT)

rectangle_button = tk.Button(tools_frame, text="Rectangle", command=lambda: select_tool("rectangle"))
rectangle_button.pack(side=tk.LEFT)

circle_button = tk.Button(tools_frame, text="Circle", command=lambda: select_tool("circle"))
circle_button.pack(side=tk.LEFT)

line_button = tk.Button(tools_frame, text="Line", command=lambda: select_tool("line"))
line_button.pack(side=tk.LEFT)

fill_button = tk.Button(tools_frame, text="Fill", command=lambda: select_tool("fill"))
fill_button.pack(side=tk.LEFT)

# Add undo and redo buttons
undo_button = tk.Button(tools_frame, text="Undo", command=undo)
undo_button.pack(side=tk.LEFT)

redo_button = tk.Button(tools_frame, text="Redo", command=redo)
redo_button.pack(side=tk.LEFT)

# Add brush size slider
brush_size_slider = tk.Scale(top_frame, from_=1, to=20, orient=tk.HORIZONTAL, label="Brush/Eraser Size", command=update_brush_size)
brush_size_slider.set(brush_size)  # Set default value
brush_size_slider.pack(side=tk.LEFT, padx=10)

# Create the canvas for drawing
canvas = tk.Canvas(root, bg="white", width=canvas_width, height=canvas_height)
canvas.pack(fill=tk.BOTH, expand=True)

# Initialize the canvas image
photo_image = ImageTk.PhotoImage(image)
canvas.create_image(0, 0, image=photo_image, anchor=tk.NW)

# Bind mouse events to the canvas for drawing and shape creation
canvas.bind("<B1-Motion>", paint)  # Mouse movement for freehand drawing or shape preview
canvas.bind("<ButtonPress-1>", start_draw)  # Start drawing when mouse is pressed
canvas.bind("<ButtonRelease-1>", finalize_shape)  # Finish drawing when mouse is released

# Start the Tkinter main loop
root.mainloop()
