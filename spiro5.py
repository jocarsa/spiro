import cv2
import numpy as np
import math
import time

# Number of arms (N) to simulate
N = 3  # Set this as needed

for i in range(0, 5):
    # Get the current epoch time for the video filename
    epoch_time = int(time.time())
    output_file = f'output_video_{epoch_time}.mp4'

    # Video configuration
    width = 1920  # Resolution
    height = 1080
    fps = 30  # FPS
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Initialize variables for each arm
    angles = np.zeros(N)
    radii = np.random.uniform(0, height // 4, N) * 1.5
    speeds = np.random.uniform(-0.5, 0.5, N) / 2

    # Initial position
    initial_x = width // 2
    initial_y = height // 2

    # Create a white background for the trace
    trace_canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background

    # Variables to store the previous point
    previous_x = None
    previous_y = None
    drawing_started = False  # Flag to avoid drawing the initial line from the center

    frame_count = 0
    minutes = 60
    max_frames = minutes * 60 * fps  # Limit to avoid infinite loop

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

        # Only draw the line if we have a valid previous point and after the drawing started
        if drawing_started:
            cv2.line(trace_canvas, (previous_x, previous_y), (x_current, y_current), (0, 0, 0), 1, cv2.LINE_AA)  # Anti-aliased line in black

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
