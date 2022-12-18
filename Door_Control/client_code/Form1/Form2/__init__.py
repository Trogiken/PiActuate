from ._anvil_designer import Form2Template
from anvil import *
import anvil.server

class Form2(Form2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def rpi_shutdown_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    check = anvil.confirm('This will Shutdown the RPI! You will not be able to reconnect', title='Shutdown RPI', large=True)
    if check:
      try:
        anvil.server.call('shutdown')
      except:
        return

  def rpi_restart_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    check = anvil.confirm('This will Restart the RPI!', title='Restart RPI', large=True)
    if check:
      try:
        anvil.server.call('shutdown', 'r')
      except:
        return

  def program_reset_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    check = anvil.confirm('Reset the config and restart the RPI', title='Reset', large=True)
    if check:
      try:
        anvil.server.call('reset_config')
        anvil.server.call('shutdown', 'r')
      except:
        return

  def program_shutdown_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    check = anvil.confirm('This will Shutdown the Program!', title='Shutdown Program', large=True)
    if check:
      try:
        # anvil.server.call('FUNC', 'PARM')
        pass
      except:
        return

  def form1_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('Form1')
