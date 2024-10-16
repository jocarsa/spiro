import cv2
import numpy as np
import math
import time
import os
import random

# Function to convert HSL to RGB
def hsl_to_rgb(h, s, l):
    h = float(h)
    s = float(s) / 100.0
    l = float(l) / 100.0
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = l - c / 2.0
    r, g, b = 0, 0, 0

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x

    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    return (r, g, b)

# Create 'videos' folder if it doesn't exist
if not os.path.exists('videos'):
    os.makedirs('videos')

# Get the current epoch time for the video filename
epoch_time = int(time.time())
output_file = os.path.join('videos', f'output_video_{epoch_time}.mp4')

# Video configuration
width = 1920  # Resolution
height = 1080
fps = 60  # Lower FPS
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Change codec
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

# Create a white background for the trace and arms canvases
trace_canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background for tracing
arms_canvas = np.ones((height, width, 3), dtype=np.uint8) * 255   # White background for arms

# Global variable to store the line width
line_width = random.randint(5, 125)  # Initialize with a random value

# Function to reset the drawing conditions and clear the screen
def reset_drawing_conditions():
    global trace_canvas, arms_canvas, line_width  # Make sure these variables are accessible and modifiable inside the function
    N = random.randint(2, 2)
    angles = np.zeros(N)
    radii = np.random.uniform(0, height // 3, N) * 1.0
    denominators = np.array([-8, -7, -6, -5, -4, -3, -2, 2, 3, 4, 5, 6, 7, 8])
    speeds = np.pi / np.random.choice(denominators, N)/10
    # Reset the canvases to white
    trace_canvas[:] = 255  # Clear trace canvas
    arms_canvas[:] = 255   # Clear arms canvas
    
    # Set a new random line width only once when resetting conditions
    line_width = random.randint(5, 125)

    return N, angles, radii, speeds

# Initialize variables for each arm
N, angles, radii, speeds = reset_drawing_conditions()

# Initial position
initial_x = width // 2
initial_y = height // 2

# Variables to store the previous point
previous_x = None
previous_y = None
drawing_started = False  # Flag to avoid drawing the initial line from the center
first_x, first_y = None, None  # To capture the first point drawn

frame_count = 0
minutes = 1
max_frames = minutes * 60 * fps  # Limit to 1 hour of frames

# Random HSL color for the trace
hue = np.random.uniform(0, 360)  # Random hue between 0 and 360
saturation = 100  # Fully saturated
lightness = 50  # Moderate lightness
trace_color = hsl_to_rgb(hue, saturation, lightness)

# Introduce the random_color parameter
random_color = random.choice([True, False])

# Start time
start_time = time.time()

try:
    while frame_count < max_frames:
        x_current = initial_x
        y_current = initial_y

        # Reset the arms canvas to be blank for each frame
        arms_canvas[:] = 255  # White background

        # Loop through each arm to calculate the position
        for j in range(N):
            # Calculate current position of the j-th arm
            cos_angle = math.cos(angles[j])
            sin_angle = math.sin(angles[j])

            new_x = x_current + int(cos_angle * radii[j])
            new_y = y_current + int(sin_angle * radii[j])

            # Draw the arm as a line from (x_current, y_current) to (new_x, new_y) in black
            cv2.line(arms_canvas, (x_current, y_current), (new_x, new_y), (0, 0, 0), 5, cv2.LINE_AA)

            # Draw black circles at each articulation point
            cv2.circle(arms_canvas, (x_current, y_current), 10, (0, 0, 0), -1)  # Black circle at articulation point
            cv2.circle(arms_canvas, (new_x, new_y), 10, (0, 0, 0), -1)  # Black circle at the next articulation point

            # Update current x and y to new_x and new_y
            x_current, y_current = new_x, new_y

            # Update the angle for the j-th arm
            angles[j] += speeds[j]

        # Capture the first point
        if drawing_started and first_x is None and first_y is None:
            first_x, first_y = previous_x, previous_y

        # Only draw the line if we have a valid previous point and after the drawing started
        if drawing_started:
            # Check the random_color flag to determine whether to draw in black or color
            if random_color:
                # Draw in black
                cv2.line(trace_canvas, (previous_x, previous_y), (x_current, y_current), (0, 0, 0), line_width, cv2.LINE_AA)
            else:
                # Use the color-changing logic
                cv2.line(trace_canvas, (previous_x, previous_y), (x_current, y_current), trace_color, line_width, cv2.LINE_AA)

        # Mark drawing as started after the first valid point
        if not drawing_started:
            drawing_started = True

        # Update the previous point to the current point
        previous_x = x_current
        previous_y = y_current

        # Normalize the trace canvas and arms canvas to range [0, 1] for multiplication
        trace_canvas_normalized = trace_canvas.astype(np.float32) / 255.0
        arms_canvas_normalized = arms_canvas.astype(np.float32) / 255.0

        # Multiply the two canvases (element-wise)
        multiplied_frame = trace_canvas_normalized * arms_canvas_normalized

        # Rescale back to [0, 255] and convert to uint8
        final_frame = (multiplied_frame * 255).astype(np.uint8)

        # Write the combined frame to the video
        out.write(final_frame)

        frame_count += 1

        # Gradually change the hue (for example, by 0.5 per frame)
        hue = (hue + 0.5) % 360
        trace_color = hsl_to_rgb(hue, saturation, lightness)

        # Check if the current point is within 5 pixels of the first point
        if first_x is not None and first_y is not None:
            distance = math.sqrt((x_current - first_x) ** 2 + (y_current - first_y) ** 2)
            if distance <= 2:
                print(f"Current point is within 5 pixels of the first point, restarting conditions.")
                # Reset the drawing conditions and continue
                N, angles, radii, speeds = reset_drawing_conditions()
                previous_x, previous_y = None, None
                drawing_started = False
                first_x, first_y = None, None

        # Print statistics every 1000 frames
        if frame_count % 1000 == 0:
            elapsed_time = time.time() - start_time
            progress = frame_count / max_frames * 100
            estimated_total_time = elapsed_time / (frame_count / max_frames)
            estimated_end_time = start_time + estimated_total_time
            remaining_time = estimated_end_time - time.time()

            print(f"Frame {frame_count}/{max_frames} - Progress: {progress:.2f}%")
            print(f"Elapsed Time: {elapsed_time:.2f} seconds")
            print(f"Estimated Total Time: {estimated_total_time:.2f} seconds")
            print(f"Estimated Time Remaining: {remaining_time:.2f} seconds")

        # Check if the user pressed the 'q' key to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Ensure the video writer and window are closed properly
    out.release()
    print(f"Video saved as {output_file}")
