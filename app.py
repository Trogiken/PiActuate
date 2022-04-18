# from door import Door
import anvil.server

# Set static IP for RPI
# Check for update button that pulls from GitHub
# Change max travel time
# Text Fields with background text like: max_travel_time: int
#   Then have a save button that changes variable values and saves it to a local file

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
    return message + '[Modified By Client]'


anvil.server.wait_forever()
