import cv2
import numpy as np
import math
import time

# Get the current epoch time for the video filename
epoch_time = int(time.time())
output_file = f'output_video_{epoch_time}.mp4'

# Video configuration
width = 1280  # Reduced resolution for performance
height = 720
fps = 30  # Reduced FPS for performance
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

# Initialize variables
angle1 = 0
radius1 = np.random.uniform(0, height // 4)
speed1 = np.random.uniform(-0.5, 0.5) / 70

angle2 = 0
radius2 = np.random.uniform(0, height // 4)
speed2 = np.random.uniform(-0.5, 0.5) / 70

initial_x = width // 2 + math.cos(angle1) * radius1 + math.cos(angle2) * radius2
initial_y = height // 2 + math.sin(angle1) * radius1 + math.sin(angle2) * radius2

# Create a white background for the trace
trace_canvas = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background

frame_count = 0
max_frames = 30000  # Limit to avoid infinite loop

# Start time
start_time = time.time()

# Create a window to display the video
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 960, 540)  # Adjust the size of the window

while frame_count < max_frames:
    # Create a white frame for each new image
    frame = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
    
    # Precompute cosine and sine for both angles
    cos_angle1 = math.cos(angle1)
    sin_angle1 = math.sin(angle1)
    cos_angle2 = math.cos(angle2)
    sin_angle2 = math.sin(angle2)
    
    # Calculate current position of the first arm
    x1 = width // 2 + int(cos_angle1 * radius1)
    y1 = height // 2 + int(sin_angle1 * radius1)
    
    # Calculate current position of the second arm
    x2 = x1 + int(cos_angle2 * radius2)
    y2 = y1 + int(sin_angle2 * radius2)
    
    # Draw the center point (black)
    cv2.circle(frame, (width // 2, height // 2), 5, (0, 0, 0), -1)  # Black center circle
    
    # Draw the first arm (black)
    cv2.line(frame, (width // 2, height // 2), (int(x1), int(y1)), (0, 0, 0), 3)  # Black arm
    cv2.circle(frame, (int(x1), int(y1)), 5, (0, 0, 0), -1)  # Black circle at the end of arm 1
    
    # Draw the second arm (black)
    cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 0), 3)  # Black arm
    cv2.circle(frame, (int(x2), int(y2)), 5, (0, 0, 0), -1)  # Black circle at the end of arm 2
    
    # Trace the point (black)
    cv2.circle(trace_canvas, (int(x2), int(y2)), 2, (0, 0, 0), -1)  # Trace point in black
    
    # Blend the frame with the trace every 10th frame
    if frame_count % 10 == 0:
        blended_frame = cv2.addWeighted(frame, 0.6, trace_canvas, 0.4, 0)
    else:
        blended_frame = frame
    
    # Write the frame to the video
    out.write(blended_frame)
    
    # Show the frame in the window every 5th frame for better performance
    if frame_count % 5 == 0:
        cv2.imshow('Frame', blended_frame)
    
    # Update angles
    angle1 += speed1
    angle2 += speed2
    
    # Check if the current point is close to the starting point
    if abs(x2 - initial_x) < 2 and abs(y2 - initial_y) < 2 and frame_count > 1000:
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
