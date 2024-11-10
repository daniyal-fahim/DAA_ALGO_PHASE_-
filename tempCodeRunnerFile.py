import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import math
import time
import threading  # Import threading for background task execution

# Load points from a file
def load_points(filename):
    points = []
    with open(filename, "r") as file:
        for line in file:
            x, y = map(int, line.strip().split())
            points.append((x, y))
    return points

# Load integers from a file
def load_integers(filename):
    with open(filename, "r") as file:
        x = int(file.readline().strip())
        y = int(file.readline().strip())
    return x, y

# Function to pause execution for visualization
def pause(seconds):
    time.sleep(seconds)

# Scale points to fit within the canvas
def scale_points(points, canvas_width, canvas_height):
    min_x = min(points, key=lambda p: p[0])[0]
    max_x = max(points, key=lambda p: p[0])[0]
    min_y = min(points, key=lambda p: p[1])[1]
    max_y = max(points, key=lambda p: p[1])[1]
    scaled_points = []
    for x, y in points:
        scaled_x = (x - min_x) / (max_x - min_x) * canvas_width
        scaled_y = (y - min_y) / (max_y - min_y) * canvas_height
        scaled_points.append((scaled_x, scaled_y))
    return scaled_points

# Adjust the canvas size based on the points
def adjust_canvas_size(points, canvas):
    min_x = min(points, key=lambda p: p[0])[0]
    max_x = max(points, key=lambda p: p[0])[0]
    min_y = min(points, key=lambda p: p[1])[1]
    max_y = max(points, key=lambda p: p[1])[1]
    padding = 20
    canvas_width = (max_x - min_x) + 2 * padding
    canvas_height = (max_y - min_y) + 2 * padding
    canvas.config(width=canvas_width, height=canvas_height)

# Draw points and the closest pair on the canvas
def draw_points(canvas, points, closest_pair=None):
    canvas.delete("all")  # Clear canvas
    scaled_points = scale_points(points, canvas.winfo_width(), canvas.winfo_height())
    for x, y in scaled_points:
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")
    
    if closest_pair:
        p1, p2 = closest_pair
        p1_scaled = scale_points([p1], canvas.winfo_width(), canvas.winfo_height())[0]
        p2_scaled = scale_points([p2], canvas.winfo_width(), canvas.winfo_height())[0]
        canvas.create_line(p1_scaled[0], p1_scaled[1], p2_scaled[0], p2_scaled[1], fill="red", width=2)

# Divide and conquer algorithm for the closest pair of points
def closest_pair_of_points(points, update_func, canvas):
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def closest_pair_recursive(points_sorted_x, points_sorted_y):
        n = len(points_sorted_x)
        if n <= 3:
            min_pair = min(((p1, p2) for i, p1 in enumerate(points_sorted_x) for p2 in points_sorted_x[i + 1:]), 
                           key=lambda pair: distance(*pair))
            update_func(f"Base case: points {min_pair} with distance {distance(*min_pair):.4f}")
            draw_points(canvas, points, min_pair)
            pause(1)
            return min_pair, distance(*min_pair)
        
        mid = n // 2
        left_x = points_sorted_x[:mid]
        right_x = points_sorted_x[mid:]
        midpoint = points_sorted_x[mid][0]
        left_y = list(filter(lambda p: p[0] <= midpoint, points_sorted_y))
        right_y = list(filter(lambda p: p[0] > midpoint, points_sorted_y))

        update_func(f"Dividing: Left = {left_x}, Right = {right_x}")
        draw_points(canvas, points)
        pause(1)
        (p1, q1), d1 = closest_pair_recursive(left_x, left_y)
        (p2, q2), d2 = closest_pair_recursive(right_x, right_y)
        
        if d1 < d2:
            min_pair, min_distance = (p1, q1), d1
        else:
            min_pair, min_distance = (p2, q2), d2

        strip = [p for p in points_sorted_y if abs(p[0] - midpoint) < min_distance]
        update_func(f"Strip: {strip}")
        draw_points(canvas, points, min_pair)
        pause(1)
        for i in range(len(strip)):
            for j in range(i + 1, min(i + 7, len(strip))):
                p1, p2 = strip[i], strip[j]
                d = distance(p1, p2)
                if d < min_distance:
                    min_pair, min_distance = (p1, p2), d
        return min_pair, min_distance

    points_sorted_x = sorted(points)
    points_sorted_y = sorted(points, key=lambda p: p[1])
    return closest_pair_recursive(points_sorted_x, points_sorted_y)

# Karatsuba algorithm for integer multiplication
def karatsuba(x, y, update_func, canvas):
    if x < 10 or y < 10:
        return x * y
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    high_x, low_x = divmod(x, 10 ** m)
    high_y, low_y = divmod(y, 10 ** m)

    update_func(f"Splitting: x = {high_x} * 10^{m} + {low_x}, y = {high_y} * 10^{m} + {low_y}")
    pause(1)
    z0 = karatsuba(low_x, low_y, update_func, canvas)
    update_func(f"z0 = {z0}")
    pause(1)
    z1 = karatsuba((low_x + high_x), (low_y + high_y), update_func, canvas)
    update_func(f"z1 = {z1}")
    pause(1)
    z2 = karatsuba(high_x, high_y, update_func, canvas)
    update_func(f"z2 = {z2}")
    pause(1)

    result = z2 * 10 ** (2 * m) + ((z1 - z2 - z0) * 10 ** m) + z0
    update_func(f"Karatsuba result: {result}")
    return result

# Run algorithm in a separate thread to keep UI responsive
def run_algorithm_in_thread(algorithm):
    # Open file dialog to load data
    filename = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text Files", "*.txt")])
    if filename:
        if "point" in filename.lower():
            points = load_points(filename)
            adjust_canvas_size(points, canvas)  # Adjust canvas size based on the points
            threading.Thread(target=algorithm, args=(points, update_func, canvas)).start()  # Run the algorithm in a new thread
        else:
            x, y = load_integers(filename)
            threading.Thread(target=algorithm, args=(x, y, update_func, canvas)).start()  # Run the algorithm in a new thread

# Update function for displaying output safely in the main thread
def update_func(text):
    root.after(0, update_output, text)  # Schedule the UI update on the main thread

# Function to update the output label text
def update_output(text):
    output_text.set(text)
    progress.start()

# Main GUI Window
root = tk.Tk()
root.title("Divide and Conquer Algorithms")
root.geometry("600x600")
root.configure(bg="#2B2B52")

# Button styles and layout
button_style = {
    "font": ("Helvetica", 12),
    "bg": "#3B3B98",
    "fg": "white",
    "activebackground": "#6F1E51",
    "activeforeground": "white",
    "width": 25,
    "bd": 2,
    "relief": "ridge"
}

label_style = {
    "font": ("Helvetica", 14),
    "bg": "#2B2B52",
    "fg": "#EAB543"
}

# Title label and buttons
title_label = tk.Label(root, text="Select an Algorithm", **label_style)
title_label.pack(pady=20)

closest_pair_button = tk.Button(root, text="Closest Pair of Points", command=lambda: run_algorithm_in_thread(closest_pair_of_points), **button_style)
closest_pair_button.pack(pady=10)

karatsuba_button = tk.Button(root, text="Karatsuba Multiplication", command=lambda: run_algorithm_in_thread(karatsuba), **button_style)
karatsuba_button.pack(pady=10)

# Output text for displaying current algorithm step (above canvas)
output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text, **label_style)
output_label.pack(pady=10)

# Canvas for displaying points and algorithm steps (shifted down)
canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True, pady=10)

# Progress bar for visualization (below canvas)
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress.pack(pady=20)

root.mainloop()
