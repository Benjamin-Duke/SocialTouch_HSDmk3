import tkinter as tk
import math

# Initialize Tkinter
root = tk.Tk()
root.title("Rectangle Matrix")

# Canvas dimensions
canvas_width = 800
canvas_height = 600
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Colors
black = "#000000"
red = "#FF0000"

# Rectangle dimensions
rect_width = 100
rect_height = 50
spacing = 20

# Calculate total matrix dimensions
matrix_width = 3 * rect_width + 4 * spacing
matrix_height = 2 * rect_height + 3 * spacing

# Calculate top-left corner to center the matrix
start_x = (canvas_width - matrix_width) // 2
start_y = (canvas_height - matrix_height) // 2

# Create a 2x3 matrix of rectangles
rectangles = []
rect_centers = []  # Store centers for distance calculation
for row in range(2):
    for col in range(3):
        x1 = start_x + col * (rect_width + spacing)
        y1 = start_y + row * (rect_height + spacing)
        x2 = x1 + rect_width
        y2 = y1 + rect_height
        rect = canvas.create_rectangle(x1, y1, x2, y2, outline=black, fill="#888888")  # Initial gray
        rectangles.append(rect)
        rect_centers.append(((x1 + x2) // 2, (y1 + y2) // 2))

# Small rectangle that can be moved with the mouse
small_rect_size = 20
# Center the small rectangle initially
small_rect_start_x = start_x + matrix_width // 2 - small_rect_size // 2
small_rect_start_y = start_y + matrix_height // 2 - small_rect_size // 2
small_rect = canvas.create_rectangle(small_rect_start_x, small_rect_start_y, small_rect_start_x + small_rect_size, small_rect_start_y + small_rect_size, fill=red)
dragging = False

# Create labels to display intensity values on the rectangles
intensity_texts = []


# Function to get the center coordinates of each rectangle
def get_rectangle_centers():
    centers = []
    for rect in rectangles:
        x1, y1, x2, y2 = canvas.coords(rect)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        centers.append((center_x, center_y))
    return centers

xc1, yc1 = get_rectangle_centers()[0]
xc2, yc2 = get_rectangle_centers()[2]
xc3, yc3 = get_rectangle_centers()[3]
xc4, yc4 = get_rectangle_centers()[5]
xc5, yc5 = get_rectangle_centers()[1]
xc6, yc6 = get_rectangle_centers()[4]


def get_Intensities(Iv, s_center_x , gamma, beta):
    if gamma < 0.5:
        alpha = (s_center_x - xc1) / (xc5 - xc1)
        I1 = (1 - alpha) * (1 - beta) * Iv
        I2 = 0
        I3 = (1-alpha) * beta * Iv
        I4 = 0
        I5 = alpha * (1 - beta) * Iv
        I6 = alpha * beta * Iv
    elif gamma > 0.5:
        alpha = (s_center_x - xc5) / (xc2 - xc5)
        I1 = 0
        I2 = alpha * (1 - beta) * Iv
        I3 = 0
        I4 = alpha * beta * Iv
        I5 = (1 - alpha) * (1 - beta) * Iv
        I6 = (1 - alpha) * beta * Iv
    elif gamma == 0.5:
        I1 = 0
        I2 = 0
        I3 = 0
        I4 = 0
        I5 = (1- beta) * Iv
        I6 = beta * Iv
    return I1, I2, I3, I4, I5, I6

def update_colors():
    """ Update rectangle colors and intensity values based on the distance to the red square. """
    # Get small rectangle center
    sx1, sy1, sx2, sy2 = canvas.coords(small_rect)
    s_center_x = (sx1 + sx2) // 2
    s_center_y = (sy1 + sy2) // 2

    # Normalize the position of the small rectangle
    gamma = (s_center_x - xc1) / (xc2 - xc1)
    alpha = 0
    beta = (s_center_y - yc1) / (yc4 - yc1)

    # Calculate the interpolated intensities
    Iv = 1  # Base intensity value
    I1, I2, I3, I4, I5, I6 = get_Intensities(Iv, s_center_x, gamma, beta)

    # Ensure intensities are non-negative
    I1 = max(I1, 0) 
    I2 = max(I2, 0)
    I3 = max(I3, 0)
    I4 = max(I4, 0)
    I5 = max(I5, 0)
    I6 = max(I6, 0)

    I1 = min(I1, 1)
    I2 = min(I2, 1)
    I3 = min(I3, 1)
    I4 = min(I4, 1)
    I5 = min(I5, 1)
    I6 = min(I6, 1)
    # Update the intensity values on the rectangles
    intensities = [I1, I5, I2, I3, I6, I4]
    for i, rect in enumerate(rectangles):
        intensity = intensities[i % 6]
        color_intensity = int(255 * intensity)  # Convert to grayscale intensity
        color = f"#{color_intensity:02x}{color_intensity:02x}{color_intensity:02x}"  # Convert to grayscale hex
        canvas.itemconfig(rect, fill=color)
        
        # Update or create text on the rectangle
        if i < len(intensity_texts):
            canvas.itemconfig(intensity_texts[i], text=f"{intensity:.2f}")
        else:
            text = canvas.create_text(rect_centers[i][0], rect_centers[i][1], text=f"{intensity:.2f}", fill="black")
            intensity_texts.append(text)

def on_mouse_down(event):
    global dragging
    if canvas.find_withtag(tk.CURRENT) == (small_rect,):
        dragging = True
        canvas.bind("<Motion>", on_mouse_move)

def on_mouse_up(event):
    global dragging
    dragging = False
    canvas.unbind("<Motion>")

def on_mouse_move(event):
    if dragging:
        new_x1 = max(start_x, min(event.x - small_rect_size // 2, start_x + matrix_width - small_rect_size))
        new_y1 = max(start_y, min(event.y - small_rect_size // 2, start_y + matrix_height - small_rect_size))
        new_x2 = new_x1 + small_rect_size
        new_y2 = new_y1 + small_rect_size
        canvas.coords(small_rect, new_x1, new_y1, new_x2, new_y2)
        update_colors()

canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# Run the Tkinter main loop
root.mainloop()
