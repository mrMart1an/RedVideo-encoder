import configparser
import os
import sys

from minecraft_classes import BarrelLayour, Coordinates


class Config:
    """Configuration class"""
    def __init__(self, config_file_path) -> None:
        """Parse a config file and return a config object"""

        # Get the config parser
        parser = configparser.ConfigParser()
        parser.read(config_file_path)


        # Parse input file settings
        input_files_cfg = parser["input_file"]

        self.input_video_file = input_files_cfg.get("input_video_file")


        # Parse output files settings
        out_files_cfg = parser["output_files"]

        self.generate_debug_video = out_files_cfg.getboolean("generate_debug_video")
        self.generate_minecraft_fun = out_files_cfg.getboolean("generate_minecraft_fun")
        self.generate_pixel_update_video = out_files_cfg.getboolean("generate_pixel_update_video")

        self.debug_video_path = out_files_cfg.get("debug_video_path")
        self.update_map_video_path = out_files_cfg.get("update_map_video_path")


        # Parse ouput screen settings
        out_screen_cfg = parser["output_screen"]

        self.x_resoulution = out_screen_cfg.getint("x_resoulution")
        self.y_resoulution = out_screen_cfg.getint("y_resoulution")
        self.output_fps_scaling = out_screen_cfg.getint("output_fps_scaling")

        self.start_frame = out_screen_cfg.getint("start_frame")
        self.finish_frame = out_screen_cfg.getint("finish_frame")


        # Parse minecraft file ouput settings
        mc_file_cfg = parser["minecraft_output"]

        functions_path = mc_file_cfg.get("functions_path")

        function_name = mc_file_cfg.get("function_name")
        function_ext = mc_file_cfg.get("function_ext")

        # Generate the file path
        self.function_file_path = os.path.join(functions_path, (function_name + function_ext))


        # Parse screen property settings
        screen_property = parser["screen_property"]

        screen_origin_str = screen_property.get("screen_origin")
        row_offset = screen_property.getint("next_row_offset")
        column_offset = screen_property.getint("next_column_offset")


        # Convert origin str to Coorinates object
        try:
            screen_origin = [int(x) for x in screen_origin_str.split(",")]

            # Check the list len
            if len(screen_origin) != 3:
                raise Exception("Screen origin shape mismatch")

            # Create Coordinates object
            self.origin = Coordinates(
                screen_origin[0],
                screen_origin[1],
                screen_origin[2]
            )

        except Exception as e:
            print(f"coordinates parsing failed: {e}")
            sys.exit(1)


        # Create the Barrel layout object
        self.barrel_layout = BarrelLayour(self.origin, row_offset, column_offset)
        
