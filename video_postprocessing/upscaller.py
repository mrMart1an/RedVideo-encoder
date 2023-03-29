import numpy as np
import cv2


# Upscale factor settings
UPSCALE_FACTOR = 10

# Path of the low resolution video to upscale
VIDEOS_DICT = {
    # input path            ouput path
    "debug.avi":         "debug_up.avi", 
    "update_map.avi":    "update_map_up.avi"
}


# Run upscalling for each video
for paths in VIDEOS_DICT.items():
    print(f"Upscaling {paths[0]}...", end="", flush=True)

    # create a video capture object
    in_cap = cv2.VideoCapture(paths[0])

    # Get fps and resolution
    fps = int(in_cap.get(cv2.CAP_PROP_FPS))
    res = [
        int(in_cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(in_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ]


    # Create the output stream
    # Create the stream
    out_cap = cv2.VideoWriter(
        paths[1],
        cv2.VideoWriter_fourcc('M','J','P','G'),
        fps,
        (res[0] * UPSCALE_FACTOR, res[1] * UPSCALE_FACTOR)
    )


    # Loop through all the frames
    while in_cap.isOpened():
        # Capture frame-by-frame
        ret, frame = in_cap.read()

        # Check for stream heath
        if ret:
            # Upscale the frame
            frame = cv2.resize(
                frame,
                (res[0] * UPSCALE_FACTOR, res[1] * UPSCALE_FACTOR), 
                interpolation = cv2.INTER_AREA
            )

            # Write the frame to the output stream
            out_cap.write(frame)

        else:
            break


    # Close the streams
    in_cap.release()
    out_cap.release()

    print(" Done")
