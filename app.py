# from door import Door
import anvil.server

# Set static IP for RPI
# Check for update button that pulls from GitHub
# Change max travel time

# use anvil to make app

# door = Door()
#
# door.move('up')
#
# door.maximum_travel_time = 10

anvil.server.connect("V5QNUE3PMZD42P7RSPOVDGL5-PTAOXCGWB7VCBPZK")


@anvil.server.callable
def show_message(message):
    print(message)


anvil.server.wait_forever()
