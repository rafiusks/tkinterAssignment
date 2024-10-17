import tkinter as tk
from tkinter import colorchooser
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageTk

# Default settings
current_color = "#000000"
current_tool = "brush"  # Default tool is brush
brush_size = 10  # Default brush size set to 10

# Lists to track actions for undo/redo
actions_stack = []
redo_stack = []

# Dictionary to hold references to tool buttons
tool_buttons = {}

# Create the main window
root = tk.Tk()
root.title("Simple Drawing Application")
root.geometry("1400x1000")

# Set default font
default_font = ("San Francisco", 12)
root.option_add("*Font", default_font)

# Tooltip class with delay and visible text
class CreateToolTip(object):
    def __init__(self, widget, text='', delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # Delay in milliseconds before showing the tooltip
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<ButtonPress>", self.hide_tooltip)

    def schedule_tooltip(self, event=None):
        self.unschedule_tooltip()
        self.id = self.widget.after(self.delay, self.show_tooltip)

    def unschedule_tooltip(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tooltip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief='solid', borderwidth=1,
            foreground="black", font=("San Francisco", 10)
        )
        label.pack(ipadx=1)
        self.id = None  # Reset the schedule ID

    def hide_tooltip(self, event=None):
        self.unschedule_tooltip()
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# Initialize the drawing surface (will be updated later)
image = None
draw = None

# Function to update the canvas image
def update_canvas():
    global photo_image
    photo_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=photo_image, anchor=tk.NW)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Function to handle canvas resizing
def resize_canvas(event):
    global image, draw
    # Get the new canvas size
    canvas_width = event.width
    canvas_height = event.height

    if image is not None:
        # Resize the image
        old_image = image
        image = Image.new("RGBA", (canvas_width, canvas_height), "white")
        old_width, old_height = old_image.size

        # Calculate the overlapping region
        paste_width = min(canvas_width, old_width)
        paste_height = min(canvas_height, old_height)
        box = (0, 0, paste_width, paste_height)

        # Crop the old image to the overlapping region
        region = old_image.crop(box)

        # Paste the cropped region into the new image
        image.paste(region, (0, 0))

        draw = ImageDraw.Draw(image)
        update_canvas()

# Function to change the color using the color picker
def choose_color(event=None):
    global current_color
    color = colorchooser.askcolor(title="Pick a color")
    if color[1] is not None:
        current_color = color[1]
        # Update the color display
        color_button.delete("all")
        color_button.create_rectangle(
            0, 0, color_button_size, color_button_size,
            fill=current_color, outline=''
        )
        update_color_status()
        update_color_history(current_color)

# Initialize color history
color_history = []

def update_color_history(color):
    if color not in color_history:
        color_history.insert(0, color)
        if len(color_history) > 5:
            color_history.pop()
        refresh_color_history()

def refresh_color_history():
    for widget in history_frame.winfo_children():
        widget.destroy()
    for color in color_history:
        swatch = tk.Canvas(
            history_frame, width=20, height=20,
            bd=1, relief='ridge'
        )
        swatch.create_rectangle(
            0, 0, 20, 20, fill=color, outline=''
        )
        # Modify the event binding to prevent propagation
        swatch.bind(
            "<Button-1>",
            lambda event, col=color: (select_preset_color(col), "break")
        )
        swatch.pack(side=tk.LEFT, padx=1)
        CreateToolTip(swatch, f"Select Color {color}")

def select_preset_color(color):
    global current_color
    current_color = color
    # Update the color display
    color_button.delete("all")
    color_button.create_rectangle(
        0, 0, color_button_size, color_button_size,
        fill=current_color, outline=''
    )
    update_color_status()
    # Do not call update_color_history here to prevent duplicates

# Function to select the drawing tool
def select_tool(tool):
    global current_tool
    current_tool = tool
    update_tool_status()
    update_button_states()

# Function to update the appearance of tool buttons
def update_button_states():
    for tool_name, button_info in tool_buttons.items():
        canvas_btn = button_info['canvas']
        circle = button_info['circle']
        if tool_name == current_tool:
            # Active button
            canvas_btn.itemconfig(circle, fill=active_color)
        else:
            # Inactive button
            canvas_btn.itemconfig(circle, fill=circle_color)

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
        x1 = event.x - brush_size / 2
        y1 = event.y - brush_size / 2
        x2 = event.x + brush_size / 2
        y2 = event.y + brush_size / 2
        draw.ellipse([x1, y1, x2, y2],
                     fill=current_color, outline=current_color)
        update_canvas()
        # For undo functionality
        actions_stack.append(image.copy())
        redo_stack.clear()  # Clear redo stack
    elif current_tool == "eraser":
        x1 = event.x - brush_size / 2
        y1 = event.y - brush_size / 2
        x2 = event.x + brush_size / 2
        y2 = event.y + brush_size / 2
        draw.rectangle([x1, y1, x2, y2],
                       fill="white", outline="white")
        update_canvas()
        # For undo functionality
        actions_stack.append(image.copy())
        redo_stack.clear()
    elif current_tool in ("rectangle", "circle", "line"):
        # Draw a shape preview
        temp_image = image.copy()
        temp_draw = ImageDraw.Draw(temp_image)
        x0, y0 = start_x, start_y
        x1, y1 = event.x, event.y
        if current_tool in ("rectangle", "circle"):
            shape_bbox = [min(x0, x1), min(y0, y1),
                          max(x0, x1), max(y0, y1)]
        else:
            shape_bbox = [x0, y0, x1, y1]
        if current_tool == "rectangle":
            temp_draw.rectangle(shape_bbox,
                                outline=current_color,
                                width=brush_size)
        elif current_tool == "circle":
            temp_draw.ellipse(shape_bbox,
                              outline=current_color,
                              width=brush_size)
        elif current_tool == "line":
            temp_draw.line(shape_bbox,
                           fill=current_color,
                           width=brush_size)
        # Update canvas with preview
        preview_image = ImageTk.PhotoImage(temp_image)
        canvas.create_image(0, 0, image=preview_image, anchor=tk.NW)
        canvas.image = preview_image  # Keep a reference

# Function to finalize shape drawing
def finalize_shape(event):
    global image, draw
    if current_tool in ("rectangle", "circle", "line"):
        x0, y0 = start_x, start_y
        x1, y1 = event.x, event.y
        if current_tool in ("rectangle", "circle"):
            shape_bbox = [min(x0, x1), min(y0, y1),
                          max(x0, x1), max(y0, y1)]
        else:
            shape_bbox = [x0, y0, x1, y1]
        if current_tool == "rectangle":
            draw.rectangle(shape_bbox,
                           outline=current_color,
                           width=brush_size)
        elif current_tool == "circle":
            draw.ellipse(shape_bbox,
                         outline=current_color,
                         width=brush_size)
        elif current_tool == "line":
            draw.line(shape_bbox,
                      fill=current_color,
                      width=brush_size)
        update_canvas()
        # For undo functionality
        actions_stack.append(image.copy())
        redo_stack.clear()
    elif current_tool == "fill":
        # Implement fill (bucket tool)
        fill_color = tuple(
            int(current_color.lstrip('#')[i:i+2], 16)
            for i in (0, 2, 4)
        ) + (255,)
        flood_fill(event.x, event.y, fill_color)
        update_canvas()
        # For undo functionality
        actions_stack.append(image.copy())
        redo_stack.clear()

# Implement flood fill algorithm
def flood_fill(x, y, fill_color):
    try:
        target_color = image.getpixel((x, y))
    except IndexError:
        return
    if target_color == fill_color:
        return

    pixel_data = image.load()
    width, height = image.size
    stack = [(x, y)]

    while stack:
        nx, ny = stack.pop()
        if nx < 0 or nx >= width or ny < 0 or ny >= height:
            continue
        current_color_at_pixel = pixel_data[nx, ny]
        if current_color_at_pixel == target_color:
            pixel_data[nx, ny] = fill_color
            stack.extend([
                (nx + 1, ny), (nx - 1, ny),
                (nx, ny + 1), (nx, ny - 1)
            ])

# Undo function
def undo(event=None):
    global image, draw
    if actions_stack:
        redo_stack.append(image.copy())
        image = actions_stack.pop()
        draw = ImageDraw.Draw(image)
        update_canvas()

# Redo function
def redo(event=None):
    global image, draw
    if redo_stack:
        actions_stack.append(image.copy())
        image = redo_stack.pop()
        draw = ImageDraw.Draw(image)
        update_canvas()

# Define the font for emojis
emoji_font = ("Apple Color Emoji", 36)
label_font = ("San Francisco", 10)

# Create the toolbar
toolbar = ttk.Frame(root, padding="5 5")
toolbar.pack(side=tk.TOP, fill=tk.X)

# Common button settings
button_size = 60
circle_radius = 28
circle_color = "#555555"
hover_color = "#777777"
active_color = "#999999"

def create_round_button(parent, emoji, command,
                        tooltip_text, label_text="", tool_name=None):
    frame = ttk.Frame(parent)
    frame.pack(side=tk.LEFT, padx=5)

    canvas_btn = tk.Canvas(
        frame, width=button_size,
        height=button_size, highlightthickness=0
    )
    # Draw circle
    circle = canvas_btn.create_oval(
        (button_size - 2 * circle_radius) // 2,
        (button_size - 2 * circle_radius) // 2,
        (button_size + 2 * circle_radius) // 2,
        (button_size + 2 * circle_radius) // 2,
        fill=active_color if tool_name == current_tool else circle_color,
        outline=""
    )
    # Add emoji text
    canvas_btn.create_text(
        button_size // 2, button_size // 2,
        text=emoji, font=emoji_font
    )
    canvas_btn.pack()
    
    # Add label under the icon
    label = ttk.Label(frame, text=label_text, font=label_font)
    label.pack()

    # Store the canvas and circle in tool_buttons
    if tool_name:
        tool_buttons[tool_name] = {'canvas': canvas_btn, 'circle': circle}

    # Bind events
    def on_click(event):
        command()

    def on_enter(event):
        if tool_name and tool_name == current_tool:
            # Active tool, keep active color
            canvas_btn.itemconfig(circle, fill=active_color)
        else:
            canvas_btn.itemconfig(circle, fill=hover_color)

    def on_leave(event):
        if tool_name and tool_name == current_tool:
            # Active tool, keep active color
            canvas_btn.itemconfig(circle, fill=active_color)
        else:
            canvas_btn.itemconfig(circle, fill=circle_color)

    canvas_btn.bind("<Button-1>", on_click)
    canvas_btn.bind("<Enter>", on_enter)
    canvas_btn.bind("<Leave>", on_leave)
    CreateToolTip(canvas_btn, tooltip_text)
    return canvas_btn

# Group 1: Drawing Tools (Brush and Eraser)
drawing_tools_frame = ttk.Frame(toolbar)
drawing_tools_frame.pack(side=tk.LEFT, padx=5)

brush_button = create_round_button(
    drawing_tools_frame,
    '🖌️',
    lambda: select_tool("brush"),
    "Brush Tool (B)",
    label_text="Brush",
    tool_name="brush"
)

eraser_button = create_round_button(
    drawing_tools_frame,
    '🩹',
    lambda: select_tool("eraser"),
    "Eraser Tool (E)",
    label_text="Eraser",
    tool_name="eraser"
)

# Separator between groups
ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
    side=tk.LEFT, fill=tk.Y, padx=5
)

# Group 2: Shape Tools (Rectangle, Circle, Line)
shape_tools_frame = ttk.Frame(toolbar)
shape_tools_frame.pack(side=tk.LEFT, padx=5)

rectangle_button = create_round_button(
    shape_tools_frame,
    '▭',
    lambda: select_tool("rectangle"),
    "Rectangle Tool (R)",
    label_text="Rectangle",
    tool_name="rectangle"
)

circle_button = create_round_button(
    shape_tools_frame,
    '⚪',
    lambda: select_tool("circle"),
    "Circle Tool (C)",
    label_text="Circle",
    tool_name="circle"
)

line_button = create_round_button(
    shape_tools_frame,
    '➖',
    lambda: select_tool("line"),
    "Line Tool (L)",
    label_text="Line",
    tool_name="line"
)

# Separator between groups
ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
    side=tk.LEFT, fill=tk.Y, padx=5
)

# Group 3: Fill Tool
fill_tools_frame = ttk.Frame(toolbar)
fill_tools_frame.pack(side=tk.LEFT, padx=5)

fill_button = create_round_button(
    fill_tools_frame,
    '🪣',
    lambda: select_tool("fill"),
    "Fill Tool (F)",
    label_text="Fill",
    tool_name="fill"
)

# Separator between groups
ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
    side=tk.LEFT, fill=tk.Y, padx=5
)

# Group 4: Action Tools (Undo and Redo)
action_tools_frame = ttk.Frame(toolbar)
action_tools_frame.pack(side=tk.LEFT, padx=5)

undo_button = create_round_button(
    action_tools_frame,
    '↩️',
    undo,
    "Undo (Cmd+Z)",
    label_text="Undo"
)

redo_button = create_round_button(
    action_tools_frame,
    '↪️',
    redo,
    "Redo (Shift+Cmd+Z)",
    label_text="Redo"
)

# Separator between groups
ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
    side=tk.LEFT, fill=tk.Y, padx=5
)

# Group 5: Color Picker and Brush Size
other_tools_frame = ttk.Frame(toolbar)
other_tools_frame.pack(side=tk.LEFT, padx=5)

# Adjust color button size
color_button_size = 50

# Add color button
color_button_frame = ttk.Frame(other_tools_frame)
color_button_frame.pack(side=tk.LEFT, padx=5)

color_button = tk.Canvas(
    color_button_frame, width=color_button_size,
    height=color_button_size, bd=1, relief='ridge'
)
color_button.create_rectangle(
    0, 0, color_button_size, color_button_size,
    fill=current_color, outline=''
)
color_button.bind("<Button-1>", choose_color)
color_button.pack()
color_label = ttk.Label(color_button_frame, text="Color", font=label_font)
color_label.pack()
CreateToolTip(color_button, "Choose Color")

# Add brush size label and slider frame
brush_size_frame = ttk.Frame(other_tools_frame)
brush_size_frame.pack(side=tk.LEFT, padx=5)

# Add min and max labels for the slider
min_label = ttk.Label(brush_size_frame, text="1")
min_label.pack(side=tk.LEFT)

# Add current brush size label
brush_size_value_label = ttk.Label(
    brush_size_frame, text=f"{brush_size}"
)
brush_size_value_label.pack(side=tk.LEFT, padx=5)

# Define update_brush_size function
def update_brush_size(value):
    global brush_size
    brush_size = max(1, int(float(value)))
    brush_size_value_label.config(text=f"{brush_size}")

# Add brush size slider
brush_size_slider = ttk.Scale(
    brush_size_frame, from_=1, to=100,
    orient=tk.HORIZONTAL, command=update_brush_size,
    length=150
)
brush_size_slider.set(brush_size)
brush_size_slider.pack(side=tk.LEFT, padx=2)
CreateToolTip(brush_size_slider, "Adjust Brush Size")

# Add max label
max_label = ttk.Label(brush_size_frame, text="100")
max_label.pack(side=tk.LEFT)

# Separator between groups
ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
    side=tk.LEFT, fill=tk.Y, padx=5
)

# Group 6: Color History Feature
history_frame = ttk.Frame(toolbar)
history_frame.pack(side=tk.LEFT, padx=5)
CreateToolTip(history_frame, "Color History")

refresh_color_history()

# Add status bar
status_bar = ttk.Frame(root, relief=tk.SUNKEN, padding="5 2")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Labels for status information
tool_status = ttk.Label(status_bar)
tool_status.pack(side=tk.LEFT, padx=5)

position_status = ttk.Label(status_bar)
position_status.pack(side=tk.LEFT, padx=5)

color_status = ttk.Label(status_bar)
color_status.pack(side=tk.LEFT, padx=5)

# Update status functions
def update_tool_status():
    tool_status.config(text=f"Tool: {current_tool.capitalize()}")

def update_position_status(event):
    position_status.config(text=f"Position: {event.x}, {event.y}")

def update_color_status():
    color_status.config(text=f"Color: {current_color}")

# Call update functions to initialize status bar
update_tool_status()
update_color_status()

# Update button states to reflect the initial tool
update_button_states()

# Create the canvas for drawing
canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

# Initialize the canvas image after the canvas is created and packed
def initialize_canvas_image(event=None):
    global image, draw
    if image is None:
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        image = Image.new(
            "RGBA", (canvas_width, canvas_height), "white"
        )
        draw = ImageDraw.Draw(image)
        update_canvas()

# Bind the initialization to the canvas size change
canvas.bind("<Configure>", initialize_canvas_image, add="+")
canvas.bind("<Configure>", resize_canvas, add="+")
canvas.bind("<Motion>", update_position_status)

# Bind mouse events to the canvas for drawing and shape creation
canvas.bind("<B1-Motion>", paint)
canvas.bind("<ButtonPress-1>", start_draw)
canvas.bind("<ButtonRelease-1>", finalize_shape)

# Create macOS-style menus (optional; you can adjust this section)
def create_macos_menus(root):
    # Remove the default Tk menu bar
    root.option_add('*tearOff', False)

    # Create the menu bar
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    # Application menu (shows as the application name on macOS)
    app_menu = tk.Menu(menu_bar, name='apple')
    menu_bar.add_cascade(menu=app_menu)

    app_menu.add_command(
        label="About Simple Drawing Application",
        command=show_about
    )
    app_menu.add_separator()
    app_menu.add_command(
        label="Quit Simple Drawing Application",
        command=root.quit, accelerator='Cmd+Q'
    )

    # File menu
    file_menu = tk.Menu(menu_bar)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(
        label="New", command=new_file, accelerator='Cmd+N'
    )
    file_menu.add_command(
        label="Open...", command=open_image, accelerator='Cmd+O'
    )
    file_menu.add_command(
        label="Save As...", command=save_image, accelerator='Cmd+S'
    )

    # Edit menu
    edit_menu = tk.Menu(menu_bar)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(
        label="Undo", command=undo, accelerator='Cmd+Z'
    )
    edit_menu.add_command(
        label="Redo", command=redo, accelerator='Shift+Cmd+Z'
    )

    # Help menu
    help_menu = tk.Menu(menu_bar)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(
        label="Simple Drawing Application Help",
        command=show_help
    )

# Implement show_about and other menu functions
def show_about():
    messagebox.showinfo(
        "About",
        "Simple Drawing Application\nCreated with Tkinter and Pillow"
    )

def new_file(event=None):
    global image, draw, actions_stack, redo_stack
    if messagebox.askyesno(
        "New File",
        "Are you sure you want to create a new file?"
        " Unsaved changes will be lost."
    ):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        image = Image.new(
            "RGBA", (canvas_width, canvas_height), "white"
        )
        draw = ImageDraw.Draw(image)
        actions_stack.clear()
        redo_stack.clear()
        update_canvas()

def open_image(event=None):
    global image, draw, actions_stack, redo_stack
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("All files", "*.*")
        ]
    )
    if file_path:
        opened_image = Image.open(file_path).convert("RGBA")
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        opened_image = opened_image.resize(
            (canvas_width, canvas_height), Image.LANCZOS
        )
        image = Image.new(
            "RGBA", (canvas_width, canvas_height), "white"
        )
        image.paste(opened_image, (0, 0))
        draw = ImageDraw.Draw(image)
        actions_stack.clear()
        redo_stack.clear()
        update_canvas()

def save_image(event=None):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
    )
    if file_path:
        image.save(file_path)

def show_help():
    messagebox.showinfo(
        "Help",
        "This is a simple drawing application."
    )

# Call the function to create menus
create_macos_menus(root)

# Update keyboard shortcuts for macOS
root.bind_all('<Command-n>', new_file)
root.bind_all('<Command-o>', open_image)
root.bind_all('<Command-s>', save_image)
root.bind_all('<Command-z>', undo)
root.bind_all('<Shift-Command-Z>', redo)
root.bind_all('<Command-q>', lambda event: root.quit())

# Function to handle keyboard shortcuts for tools
def bind_tool_shortcuts():
    root.bind('b', lambda event: select_tool('brush'))
    root.bind('e', lambda event: select_tool('eraser'))
    root.bind('r', lambda event: select_tool('rectangle'))
    root.bind('c', lambda event: select_tool('circle'))
    root.bind('l', lambda event: select_tool('line'))
    root.bind('f', lambda event: select_tool('fill'))

bind_tool_shortcuts()

# Start the Tkinter main loop
root.mainloop()
