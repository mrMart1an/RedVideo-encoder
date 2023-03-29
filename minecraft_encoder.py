import numpy as np

from video_processing import MCBuffer
from minecraft_classes import Barrel, Shulker, SHULKER_SLOTS, BARREL_SLOTS
from settings import Config




class ItemBuffer:
    """Store the encoded items list"""
    def __init__(self, config: Config) -> None:
        # Get the screen resolution
        self.x_res = config.x_resoulution
        self.y_res = config.y_resoulution

        # Generate the internal buffer
        self.__buffer = [[] for _ in range(0, self.x_res * self.y_res)]



    def append_item(self, index, color, count):
        """Save an item in the buffer"""
        # Calculate index
        index = index[1] + (index[0] * self.y_res)

        # Append item to the pixel list
        self.__buffer[index].append((color, count))



    def get_pixel_list(self, x, y):
        """Return the list of items for a given pixel"""
        # Calculate index
        index = x + (y * self.y_res)

        # Return the list
        return self.__buffer[index]




class MCencoder:
    """Encode the video for the minecraft sceen"""
    def __init__(self, video_buf: MCBuffer, config: Config) -> None:
        # Get the buffer and property
        self.video_buffer = video_buf.video_buf
        self.video_frames = video_buf.output_frames

        # Store the settings
        self.config = config

        # Create the items list array
        self.items_buffer = ItemBuffer(config)



    def __encode_to_items(self):
        """
        Transform the video into a list of items that will later be used to fill the data shulker
        """
        # Used to count the number of frame from the last pixel update
        counter_matrix = np.zeros(
            (self.config.y_resoulution, self.config.x_resoulution),
            np.dtype("uint8")
        )
        # Matrix for incrementing the counters
        inc_matrix = np.ones(
            (self.config.y_resoulution, self.config.x_resoulution),
            np.dtype("uint8")
        )

        # Store the previous frame in the loop
        last_frame = self.video_buffer[0]


        # Loop through all frames
        for i in range(1, self.video_frames):
            # Get the new frame and check for updates
            frame = self.video_buffer[i]
            update_map = frame != last_frame

            # Increment the counter
            counter_matrix += inc_matrix


            # Get the indices of the updated pixel
            # or the pixel that stayed unupdated for more that 64 frame
            indices_outer, indices_inner = np.where(
                np.logical_or(update_map, counter_matrix >= 64)
            )

            # Process the indices
            for i, indices_outer in enumerate(indices_outer):
                # Get the index
                index = (indices_outer, indices_inner[i])

                # Append item to pixel list
                self.items_buffer.append_item(
                    index,
                    last_frame[index],
                    counter_matrix[index]
                )

                # Reset the counter
                counter_matrix[index] = 0


            # Update last frame
            last_frame = frame


        # Process the last frame
        # Increment the counter
        counter_matrix += inc_matrix

        # Save items for all of the pixel
        for x in range(0, self.config.x_resoulution):
            for y in range(0, self.config.y_resoulution):
                # Get the index
                index = (y, x)

                # Append item to pixel list
                self.items_buffer.append_item(
                    index,
                    last_frame[index],
                    counter_matrix[index]
                )



    def save_mc_function(self):
        """
        Save the Minecraft function to program the screen
        Use the path specified in the config file
        """
        # Generate the items buffer
        print("Encoding video to items... ", end="", flush=True)
        self.__encode_to_items()
        print("Done")


        # Open the function file
        with open(self.config.function_file_path, "w", encoding="utf8") as f:
            print("Generating the minecraft function... ", end="", flush=True)

            # Process all the pixel
            for x in range(0, self.config.x_resoulution):
                for y in range(0, self.config.y_resoulution):
                    # Generate a new barrel with the pixel coordintes
                    barrel = Barrel(x, y, self.config.barrel_layout)
                    # Generate the first shulker
                    shulker = Shulker()

                    # Reset shulker and barrel slots counter
                    s_counter, b_counter = 0, 0


                    # Add each item to a shulker
                    for items in self.items_buffer.get_pixel_list(x, y):
                        # Fill shulker slot with items and increment slots counter
                        shulker.fill_slot(s_counter, items[0], items[1])
                        s_counter += 1

                        # When the shulker is full add it to the barrel and create a new one
                        if s_counter == SHULKER_SLOTS:
                            # Add shulker to barrel and icrement slots counter
                            barrel.fill_slot(b_counter, shulker)
                            b_counter += 1

                            # Get new empy shulker and reset slots counter
                            shulker = Shulker()
                            s_counter = 0

                            # Check for overflow of the barrel
                            if b_counter == BARREL_SLOTS:
                                raise Exception("The video can't fit in screen memory")


                    # At the end of the loop add the last shulker to the barrel
                    barrel.fill_slot(b_counter, shulker)


                    # Save the barrel ouput on the file
                    f.write(barrel.return_barrel())


            # Terminate the file with a command to kill all the entity
            # produce by the setblock commands
            f.write("kill @e[type=minecraft:item]")

        print("Done")
        
