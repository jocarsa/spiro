import cv2
import numpy as np
import math
import time

for i in range(0,5):
    # Get the current epoch time for the video filename
    epoch_time = int(time.time())
    output_file = f'output_video_{epoch_time}.mp4'

    # Video configuration
    width = 1920  # Resolution
    height = 1080
    fps = 30  # FPS
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Initialize variables
    angle1 = 0
    radius1 = np.random.uniform(0, height // 4)*1.5
    speed1 = np.random.uniform(-0.5, 0.5) / 2

    angle2 = 0
    radius2 = np.random.uniform(0, height // 4)*1.5
    speed2 = np.random.uniform(-0.5, 0.5) / 2

    # Initial positions
    initial_x = width // 2 + math.cos(angle1) * radius1 + math.cos(angle2) * radius2
    initial_y = height // 2 + math.sin(angle1) * radius1 + math.sin(angle2) * radius2

    # Create a white background for the trace
    trace_canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background

    # Variables to store the previous point
    previous_x2 = int(initial_x)
    previous_y2 = int(initial_y)

    frame_count = 0
    minutes = 60
    max_frames = minutes*60*fps  # Limit to avoid infinite loop

    # Start time
    start_time = time.time()

    # Create a window to display the video
    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', 960, 540)  # Adjust the size of the window

    while frame_count < max_frames:
        # Precompute cosine and sine for both angles
        cos_angle1 = math.cos(angle1)
        sin_angle1 = math.sin(angle1)
        cos_angle2 = math.cos(angle2)
        sin_angle2 = math.sin(angle2)
        
        # Calculate current position of the first arm (not drawn)
        x1 = width // 2 + int(cos_angle1 * radius1)
        y1 = height // 2 + int(sin_angle1 * radius1)
        
        # Calculate current position of the second arm
        x2 = x1 + int(cos_angle2 * radius2)
        y2 = y1 + int(sin_angle2 * radius2)
        
        # Draw a line from the previous point to the current point
        cv2.line(trace_canvas, (previous_x2, previous_y2), (x2, y2), (0, 0, 0), 2)  # Line in black
        
        # Write the trace directly to the video
        out.write(trace_canvas)
        
        # Show the trace in the window
        cv2.imshow('Frame', trace_canvas)
        
        # Update angles
        angle1 += speed1
        angle2 += speed2
        
        # Update the previous point to the current point
        previous_x2 = x2
        previous_y2 = y2
        
        # Check if the current point is close to the starting point
        if abs(x2 - initial_x) < 2 and abs(y2 - initial_y) < 5 and frame_count > 1000:
            break
        
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
