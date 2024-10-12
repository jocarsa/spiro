import cv2
import numpy as np
import math
import time
import os

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

# Number of arms (N) to simulate
N = 2  # Set this as needed

# Create 'videos' folder if it doesn't exist
if not os.path.exists('videos'):
    os.makedirs('videos')

for i in range(0, 25):
    # Get the current epoch time for the video filename
    epoch_time = int(time.time())
    output_file = os.path.join('videos', f'output_video_{epoch_time}.mp4')

    # Video configuration
    width = 1920  # Resolution
    height = 1080
    fps = 60  # FPS
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Initialize variables for each arm
    angles = np.zeros(N)
    radii = np.random.uniform(0, height // 4, N) * 1.5
    speeds = np.random.uniform(-0.5, 0.5, N) / 20

    # Initial position
    initial_x = width // 2
    initial_y = height // 2

    # Create a white background for the trace
    trace_canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background

    # Variables to store the previous point
    previous_x = None
    previous_y = None
    drawing_started = False  # Flag to avoid drawing the initial line from the center
    first_x, first_y = None, None  # To capture the first point drawn

    frame_count = 0
    minutes = 60
    max_frames = minutes * 60 * fps  # Limit to avoid infinite loop

    # Random HSL color for the trace
    hue = np.random.uniform(0, 360)  # Random hue between 0 and 360
    saturation = 100  # Fully saturated
    lightness = 50  # Moderate lightness
    trace_color = hsl_to_rgb(hue, saturation, lightness)

    # Start time
    start_time = time.time()

    # Create a window to display the video
    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', 960, 540)  # Adjust the size of the window

    while frame_count < max_frames:
        x_current = initial_x
        y_current = initial_y

        # Loop through each arm to calculate the position
        for j in range(N):
            # Calculate current position of the j-th arm
            cos_angle = math.cos(angles[j])
            sin_angle = math.sin(angles[j])

            x_current += int(cos_angle * radii[j])
            y_current += int(sin_angle * radii[j])

            # Update the angle for the j-th arm
            angles[j] += speeds[j]

        # Capture the first point
        if drawing_started and first_x is None and first_y is None:
            first_x, first_y = previous_x, previous_y

        # Only draw the line if we have a valid previous point and after the drawing started
        if drawing_started:
            cv2.line(trace_canvas, (previous_x, previous_y), (x_current, y_current), trace_color, 5, cv2.LINE_AA)  # Anti-aliased line

        # Mark drawing as started after the first valid point
        if not drawing_started:
            drawing_started = True

        # Write the trace directly to the video
        out.write(trace_canvas)

        # Show the trace in the window
        cv2.imshow('Frame', trace_canvas)

        # Update the previous point to the current point
        previous_x = x_current
        previous_y = y_current

        frame_count += 1

        # Gradually change the hue (for example, by 0.5 per frame)
        hue = (hue + 0.5) % 360
        trace_color = hsl_to_rgb(hue, saturation, lightness)

        # Check if the current point is within 5 pixels of the first point
        if first_x is not None and first_y is not None:
            distance = math.sqrt((x_current - first_x) ** 2 + (y_current - first_y) ** 2)
            if distance <= 2:
                print(f"Current point is within 5 pixels of the first point, stopping the video.")
                break

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

    # Release the video writer and close the window
    out.release()
    cv2.destroyAllWindows()

    print(f"Video saved as {output_file}")
