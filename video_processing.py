import numpy as np
import cv2

from settings import Config


class MCBuffer:
    """Store and process the video stream"""
    def __init__(self, config: Config) -> None:
        """
        Read the input video file, process it and store it in RAM as a np array
        """
        # Get a reference to the config object
        self.config = config

        # Get input file
        input_video_path = config.input_video_file

        # create a video capture object and get the original video fps
        cap = cv2.VideoCapture(input_video_path)
        self.original_fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.output_fps = self.original_fps // config.output_fps_scaling

        # Check video stream health
        if cap.isOpened() == False:
            raise Exception("Error during video file loading")


        # Get the output resolution
        self.out_res = [config.x_resoulution, config.y_resoulution]


        # Get video starting and ending point
        # Ending point
        if config.finish_frame == -1:
            self.video_end = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        elif config.finish_frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT)):
            self.video_end = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        else:
            self.video_end = config.finish_frame

        # Starting point
        if config.start_frame > int(cap.get(cv2.CAP_PROP_FRAME_COUNT)):
            raise Exception("video starting point out of bound")
        elif config.start_frame >= self.video_end:
            raise Exception("video starting point >= ending point")

        else:
            self.video_start = config.start_frame


        # Calculate the number of ouput frames
        input_frames = self.video_end - self.video_start
        # If input_frames is a multiple of the scaling factor don't add 1
        if input_frames % config.output_fps_scaling == 0:
            self.output_frames = input_frames // config.output_fps_scaling
        else:
            self.output_frames = (input_frames // config.output_fps_scaling) + 1

        # Create the video buffer
        self.video_buf = np.zeros(
            (self.output_frames, self.out_res[1], self.out_res[0]),
            np.dtype('uint8')
        )

        buf_counter = 0


        # Load the processed video in the buffer
        print(f"Loading {input_video_path} to RAM... ", end="", flush=True)
        for i in range(0, self.video_end):
            # Capture frame-by-frame
            ret, frame = cap.read()

            # check if video start is reached
            if i >= self.video_start:
                # Process frame
                if i % config.output_fps_scaling == 0:
                    self.video_buf[buf_counter] = self.__process_frame(frame)
                    buf_counter += 1    # increment the counter


            # Check the health of the steam
            if (not ret) or (not cap.isOpened()):
                break


        # When everything done, release the video capture object
        cap.release()
        print("Done")



    def __process_frame(self, frame):
        """Convert a frame into a numpy array with output property"""
        # To gray scale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Resize the frame
        new_x = self.out_res[0]
        new_y = self.out_res[1]

        frame = cv2.resize(frame, (new_x, new_y), interpolation=cv2.INTER_AREA)

        # Convert the frame to a binary set of 0 and 1
        _, frame = cv2.threshold(frame ,127,255, cv2.THRESH_BINARY)
        frame = frame // 255

        # Return the processed frame
        return frame



    def generate_debug_video(self):
        """
        Save the processed video buffer to the input file
        """
        # Create the stream
        debug_video_cap = cv2.VideoWriter(
            self.config.debug_video_path,
            cv2.VideoWriter_fourcc('M','J','P','G'),
            self.output_fps,
            (self.out_res[0], self.out_res[1])
        )

        # Write the video on the stream
        print("Generating debug video... ", end="", flush=True)
        for i in range(0, len(self.video_buf)):
            # To color imgage
            frame = self.video_buf[i] * 255
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # Write frame on stream
            debug_video_cap.write(frame)


        # Close the stream
        debug_video_cap.release()
        print("Done")



    def generate_update_map_video(self):
        """
        Generate the pixel update map for the video
        and save to the specified file
        """
        # Create the stream
        update_map_cap = cv2.VideoWriter(
            self.config.update_map_video_path,
            cv2.VideoWriter_fourcc('M','J','P','G'),
            self.output_fps,
            (self.out_res[0], self.out_res[1])
        )

        last_frame = self.video_buf[0]

        # Loop throug all the frame
        print("Generating update map video... ", end="", flush=True)
        for i in range(1, len(self.video_buf)):
            # Produce the pixel update frame and convert it to color
            frame = np.where(self.video_buf[i] != last_frame, 255, 0)
            frame = frame.astype(np.dtype("uint8"))

            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            update_map_cap.write(frame)

            # Save last frame for the next frame
            last_frame = self.video_buf[i]


        # Close the stream
        update_map_cap.release()
        print("Done")

