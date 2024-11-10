import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
import math
import time
import threading

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

# Draw points and the closest pair on the canvas
def draw_points(canvas, points, closest_pair=None):
    canvas.delete("all")  # Clear canvas

    # Draw points
    for x, y in points:
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")
    
    if closest_pair:
        # Draw the closest pair in red
        p1, p2 = closest_pair
        canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="red", width=2)

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
            pause(1)  # Pause for 1 second for visualization
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

# Function to dynamically adjust the canvas size based on points
def adjust_canvas_size(points):
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)
    
    # Set canvas size to accommodate all points, with some padding
    canvas.config(width=max_x + 50, height=max_y + 50)

# Main GUI Window with Improved Theme
root = tk.Tk()
root.title("Divide and Conquer Algorithms")
root.geometry("600x600")
root.configure(bg="#2B2B52")

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

# Title Label
title_label = tk.Label(root, text="Select an Algorithm", **label_style)
title_label.pack(pady=10)

# Frame for buttons
button_frame = tk.Frame(root, bg="#2B2B52")
button_frame.pack(pady=20)

# Button for Closest Pair of Points
closest_pair_button = tk.Button(button_frame, text="Run Closest Pair of Points", command=lambda: run_algorithm(closest_pair_of_points), **button_style)
closest_pair_button.grid(row=0, column=0, padx=10, pady=5)

# Button for Karatsuba Multiplication
karatsuba_button = tk.Button(button_frame, text="Run Karatsuba Multiplication", command=lambda: run_algorithm(karatsuba), **button_style)
karatsuba_button.grid(row=1, column=0, padx=10, pady=5)

# Output Label
output_text = tk.StringVar()
output_text.set("Results will be displayed here.")
output_label = tk.Label(root, textvariable=output_text, font=("Helvetica", 12), bg="#2B2B52", fg="white", wraplength=450, justify="left")
output_label.pack(pady=10)

# Progress bar for visualization
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="indeterminate")
progress.pack(pady=10)

# Frame for Canvas (graph)
canvas_frame = tk.Frame(root)
canvas_frame.pack(pady=10)

# Canvas for visualization of points
canvas = tk.Canvas(canvas_frame, width=800, height=600, bg="white")  # Increased size for better visibility
canvas.grid(row=0, column=0)

# Algorithm runner function
def run_algorithm(algorithm_func):
    file_path = filedialog.askopenfilename(title="Select Input File", filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return
    progress.start()
    
    # Using threading to run the algorithm without freezing the GUI
    threading.Thread(target=execute_algorithm, args=(algorithm_func, file_path)).start()

# Execute the algorithm in a separate thread
def execute_algorithm(algorithm_func, file_path):
    if algorithm_func == closest_pair_of_points:
        points = load_points(file_path)
        adjust_canvas_size(points)  # Adjust canvas size before drawing
        result = algorithm_func(points, update_func, canvas)
        output_text.set(f"Closest Pair of Points: {result[0]}\nDistance: {result[1]:.4f}")
    elif algorithm_func == karatsuba:
        x, y = load_integers(file_path)
        result = algorithm_func(x, y, update_func, canvas)
        output_text.set(f"Product: {result}")
    progress.stop()

# Update function for showing algorithm steps
def update_func(message):
    output_text.set(message)
    root.update_idletasks()

root.mainloop()
