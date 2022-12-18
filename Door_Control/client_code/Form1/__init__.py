from ._anvil_designer import Form1Template
from anvil import *
from time import sleep
import anvil.server

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    self.active_sunrise = ''
    self.active_sunset = ''
    self.sunrise_offset = ''
    self.sunset_offset = ''
    self.automation_enabled = False
    
    self.lockout = False
    self.first_load = True
    
    anvil.set_default_error_handling(self.rpi_status())

#### LINKS ####
  def form2_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('Form1.Form2')
#### LINKS ####

#### GLOBAL FUNCTIONS ####
  def rpi_status(self):
    try:
      anvil.server.call_s('rpi_status')
      self.app_lockout(False)
      if self.first_load:
        self.update_data()
        self.first_load = False
      return True
    except Exception:
      self.app_lockout(True)
      return False
  
  def app_lockout(self, opt):
    if opt is True:
      if self.lockout is not True:
        self.door_status_updater.interval = 0  # Disabled status updater
        self.offset_selection_dropdown.enabled = False
        self.door_up_button.enabled = False
        self.door_down_button.enabled = False
        self.automation_checkbox.enabled = False
        self.offset_update_button.enabled = False
        self.offset_set_button.enabled = False
        self.door_auxiliary_checkbox.enabled = False
        
        anvil.alert('Program is not online', title='Offline')
        self.lockout = True
    elif opt is False:
      if self.lockout is True:
        self.door_status_updater.interval = 1  # Enable status updater
        self.offset_selection_dropdown.enabled = True
        self.door_up_button.enabled = True
        self.door_down_button.enabled = True
        self.automation_checkbox.enabled = True
        self.offset_update_button.enabled = True
        self.offset_set_button.enabled = True
        self.door_auxiliary_checkbox.enabled = True
        
        anvil.alert('Program online', title='Online')
        self.lockout = False
    else:
      raise 'Invalid Option'  # Option not True or False

  def update_data(self):
    c_state = anvil.server.call('c_state')
    get_times = anvil.server.call('get_times')

    automation_enabled = c_state['automation']
    aux_enabled = c_state['auxiliary']
    
    # Change required display values
    self.automation_checkbox.checked = automation_enabled
    self.door_auxiliary_checkbox.checked = aux_enabled
    
    if automation_enabled:
      self.sunrise_offset = c_state['sunrise_offset']
      self.sunset_offset = c_state['sunset_offset']
      self.active_sunrise = get_times['sunrise']
      self.active_sunset = get_times['sunset']
      self.offset_card.visible = True
      self.door_up_button.enabled = False
      self.door_down_button.enabled = False
      
      if self.offset_selection_dropdown.selected_value == 'Sunrise':
        if self.sunrise_offset > 0:
          self.offset_time.text = '+' + str(self.sunrise_offset)
        elif self.sunrise_offset == 0:
          self.offset_time.text = self.sunrise_offset
        else:
          self.offset_time.text = '-' + str(self.sunrise_offset)
        
        self.current_time.text = self.active_sunrise
      else:
        if self.sunset_offset > 0:
          self.offset_time.text = '+' + str(self.sunset_offset)
        elif self.sunset_offset == 0:
          self.offset_time.text = self.sunset_offset
        else:
          self.offset_time.text = '-' + str(self.sunset_offset)
        
        self.current_time.text = self.active_sunset
    else:
      self.offset_card.visible = False
      self.door_up_button.enabled = True
      self.door_down_button.enabled = True
#### GLOBAL FUNCTIONS ####

#### TIMERS ####
  def door_status_updater_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    try:
      response = anvil.server.call_s('door_status')
      self.door_status_placeholder.content = response.upper()
    except:
      return

  def rpi_status_check_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    self.rpi_status()
#### TIMERS ####

########## DOOR CONTROL CARD ##########
  def door_up_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('move', 2)

  def door_down_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('move', 1)

  def door_auxiliary_checkbox_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    if self.door_auxiliary_checkbox.checked:
      anvil.server.call_s('change', 'auxiliary', True)
      anvil.server.call('run_aux')
    else:
      anvil.server.call_s('change', 'auxiliary', False)
      anvil.server.call('stop_aux')
    
    self.update_data()
########## DOOR CONTROL CARD ##########

########## AUTOMATION CARD ##########
  def automation_checkbox_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    if self.automation_checkbox.checked:
      anvil.server.call_s('change', 'automation', True)
      anvil.server.call('run_auto')
    else:
      anvil.server.call_s('change', 'automation', False)
      anvil.server.call('stop_auto')
    
    self.update_data()

  def offset_selection_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.offset_selection_dropdown.selected_value == 'Sunrise':
      if self.sunrise_offset > 0:
        self.offset_time.text = '+' + str(self.sunrise_offset)
      elif self.sunrise_offset == 0:
        self.offset_time.text = str(self.sunrise_offset)
      else:
        self.offset_time.text = str(self.sunrise_offset)
        
      self.current_time.text = self.active_sunrise
    else:
      if self.sunset_offset > 0:
        self.offset_time.text = '+' + str(self.sunset_offset)
      elif self.sunset_offset == 0:
        self.offset_time.text = str(self.sunset_offset)
      else:
        self.offset_time.text = str(self.sunset_offset)
        
      self.current_time.text = self.active_sunset

  def offset_value_box_change(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    try:
      int(self.offset_value_box.text)
    except Exception:
      self.offset_value_box.text = ''

  def offset_value_box_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.offset_set_button_click()

  def offset_set_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    offset_value = self.offset_value_box.text
    self.offset_value_box.text = ''
    
    if self.offset_pos_neg_dropdown.selected_value == '+':
      if self.offset_selection_dropdown.selected_value == 'Sunrise':
        self.sunrise_offset = int(offset_value)
        self.offset_time.text = '+' + str(self.sunrise_offset)
      else:
        self.offset_time.text = '+' + str(self.sunset_offset)
        self.sunset_offset = int(offset_value)
    else:
        if self.offset_selection_dropdown.selected_value == 'Sunrise':
          self.sunrise_offset = -int(offset_value)
          self.offset_time.text = str(self.sunrise_offset)
        else:
          self.sunset_offset = -int(offset_value)
          self.offset_time.text = str(self.sunset_offset)

  def offset_update_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    r = int(self.sunrise_offset)
    s = int(self.sunset_offset)
    anvil.server.call('change_rise', r)
    anvil.server.call('change_set', s)
    
    anvil.server.call('refresh_auto')
    sleep(1)
    self.update_data()
########## AUTOMATION CARD ##########