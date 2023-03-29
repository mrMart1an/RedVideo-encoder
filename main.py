from settings import Config
from video_processing import MCBuffer
from minecraft_encoder import MCencoder


# Parse the settings file
cfg = Config("config.cfg")

# Load and process the input video
buf = MCBuffer(cfg)


# Generate the output debug files
if cfg.generate_debug_video:
    buf.generate_debug_video()
if cfg.generate_pixel_update_video:
    buf.generate_update_map_video()


# Create the video encoder
encoder = MCencoder(buf, cfg)

# Generate the minecraft output function
if cfg.generate_minecraft_fun:
    encoder.save_mc_function()

