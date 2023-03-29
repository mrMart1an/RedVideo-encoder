# Portion of command to fill one slot of a shulker box
ITEM_CMD = "{Slot:#item_slot,id:#item_Id,Count:#count}"
# Portion of command to put a shulker in a barrel slot 
SHULKER_CMD = "{Slot:#shulker_slot,id:white_shulker_box,Count:1,tag:{BlockEntityTag:{Items:[#shulker_item]}}}"
# Portion of the command to place a prefilled barrel
BARREL_CMD = "setblock #cord minecraft:barrel[facing=east]{Items:[#barrel_item]} destroy\n"



# Shulker and barrel dimension
SHULKER_SLOTS = 27
BARREL_SLOTS = 27


# Encoding items dictionary
ITEM_ID_DICT = {
    0: "black_wool",
    1: "white_wool"
}




class Coordinates:
    """Dataclass to rappresent minecraft coordinates"""
    def __init__(self, x = 0, y = 0, z = 0) -> None:
        self.X = x
        self.Y = y
        self.Z = z



    def format(self):
        """Return the coordinate as a string"""
        return f"{self.X} {self.Y} {self.Z}"


class BarrelLayour:
    """Store the layout of the barrels behind the screen"""
    def __init__(self, origin: Coordinates, row_offset, column_offset) -> None:
        self.origin = origin

        self.row_offset = row_offset
        self.column_offset = column_offset



    def pixel_to_ingame(self, x, y):
        """
        Calculate the coordinates of the in game barrel for a given pixel
        Take the pixel coordinates as input
        Return a Coordinates object for the barrel
        """
        # Generate the output object
        output = Coordinates()
        output.X = self.origin.X

        # Calculate the offsetted coordinates
        output.Y = self.origin.Y + ( y * self.row_offset )
        output.Z = self.origin.Z + ( x * self.column_offset )

        # Return the coordinates
        return output




class Shulker:
    """A minecraft shulker object"""
    def __init__(self) -> None:
        # List of command for the items in each slot
        self.items_cmds = [None] * SHULKER_SLOTS



    def fill_slot(self, slot, color, amount):
        """
        Fill a slot with the right amount of black or white wool
        Color is either 0 or 1
        """
        # Get the item id from the dictionary
        item_id = ITEM_ID_DICT[color]

        # Generate the items command
        i_cmd = ITEM_CMD

        i_cmd = i_cmd.replace("#item_slot", str(slot))
        i_cmd = i_cmd.replace("#item_Id", item_id)
        i_cmd = i_cmd.replace("#count", str(amount))

        # Fill the slot with the command
        self.items_cmds[slot] = i_cmd



    def return_shulker(self, barrel_slot):
        """
        Return the command to create a shulker in a specific barrel slot
        """

        cmds = []
        output = SHULKER_CMD

        # If the slot is empy remove it from the output
        for i in self.items_cmds:
            if i is not None:
                cmds.append(i)

        # Concatenate all the itmes commands
        items = ",".join(cmds)

        # Create the final command
        output = output.replace("#shulker_slot", str(barrel_slot))
        output = output.replace("#shulker_item", items)

        # Return the composed command
        return output




class Barrel:
    """A minecraft barrel object"""
    def __init__(self, x, y, layout: BarrelLayour) -> None:
        """
        Create a Minecraft barrel object to store the shulker box.
        Take the pixel coordinates as an input 
        and calculate the in-game position of the barrel 
        """
        # Get the barrel coordinates
        self.coordinates = layout.pixel_to_ingame(x, y)

        # List of command for the shulker in each slot
        self.items_cmds = [None] * BARREL_SLOTS



    def fill_slot(self, slot, shulker: Shulker):
        """
        Fill a slot with the right amount of black or white wool
        Color is either 0 or 1
        """
        # Generate the shulker command
        shulker_cmd = shulker.return_shulker(slot)

        # Fill the slot with the command
        self.items_cmds[slot] = shulker_cmd



    def return_barrel(self):
        """
        Return the command to place the barrel
        """
        cmds = []
        output = BARREL_CMD

        # If the slot is empy remove it from the output
        for i in self.items_cmds:
            if i is not None:
                cmds.append(i)

        # Concatenate all the itmes commands
        items = ",".join(cmds)

        # Create the final command
        output = output.replace("#cord", self.coordinates.format())
        output = output.replace("#barrel_item", items)

        # Return the composed command
        return output
        