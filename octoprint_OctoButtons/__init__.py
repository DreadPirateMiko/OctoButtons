# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.settings
from gpiozero import Button
from gpiozero import PiBoardInfo
import gpiozero
import string
import time
import threading
import os

class OctoButtons( octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin):


    def __init__(self):
        self._pin_to_gpio_rev1 = [-1, -1, -1, 0, -1, 1, -1, 4, 14, -1, 15, 17, 18, 21, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ]
        self._pin_to_gpio_rev2 = [-1, -1, -1, 2, -1, 3, -1, 4, 14, -1, 15, 17, 18, 27, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 ]
        self._pin_to_gpio_rev3 = [-1, -1, -1, 2, -1, 3, -1, 4, 14, -1, 15, 17, 18, 27, -1, 22, 23, -1, 24, 10, -1, 9, 25, 11, 8, -1, 7, -1, -1, 5, -1, 6, 12, 13, -1, 19, 16, 26, 20, -1, 21 ]

        self.GPIOMode = ''
        self._configuredButton = []
        self._settingsGPIOPins = []
        self.button_definitions = {}

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            button_definitions = []
        )
        
    def on_settings_initialized(self):
        self.reload_button_definitions();
        
        self._helpers = self._plugin_manager.get_helpers("psucontrol","turn_psu_on","turn_psu_off","get_psu_state")
        self._logger.info(self._helpers)
        if self._helpers:
            if "turn_psu_on" in self._helpers:
                self.turn_psu_on = self._helpers["turn_psu_on"]
            if "turn_psu_off" in self._helpers:
                self.turn_psu_off = self._helpers["turn_psu_off"]
            if "get_psu_state" in self._helpers:
                self.get_psu_state = self._helpers["get_psu_state"]
    
    def reload_button_definitions(self):
        self.button_definitions = {}

        button_definitions_tmp = self._settings.get(["button_definitions"])
        self._logger.debug("button_definitions: %s" % button_definitions_tmp)

        for definition in button_definitions_tmp:
#            self.button_definitions[definition['action']] = dict(type=definition['type'], command=definition['command'], enabled=definition['enabled'])
#            self._logger.info("Add Button definition 'GPIO:%s' = %s %s %s %s " % (definition['GPIO'], definition['type'], definition['axis'], definition['dist'], definition['action']))
            self.button_definitions[definition['GPIO']] = definition #dict(type=definition['type'], axis=definition['axis'], dist=definition['dist'], action=definition['action'], enabled=definition['enabled'])
            self._configure_button(int(definition['GPIO']))

        self._logger.info(self.button_definitions)
        
    def _configure_button(self,pin):
        self._logger.info("Configuring GPIO for pin %s (%s)" % (pin, self.button_definitions[pin]['type']))
        try:
            button = Button(self._gpio_board_to_bcm(pin),hold_time=0.1)
            if self.button_definitions[pin]['type'] == 'psu':
                button.when_held = self._toggle_psu
            elif self.button_definitions[pin]['type'] == 'jog':
                button.when_pressed = self._jog
            elif self.button_definitions[pin]['type'] == 'home':
                button.when_pressed = self._home
            elif self.button_definitions[pin]['type'] == 'action':
                button.when_pressed = self._action
            elif self.button_definitions[pin]['type'] == 'gcode':
                button.when_pressed = self._gcode
               
            self._configuredButton.append(button)

        except (RuntimeError, ValueError) as e:
            self._logger.error(e)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_button_definitions()
        
    # def get_settings_version(self):
        # return 1
        
    def get_template_configs(self):
        return [
            # dict(type="navbar", custom_bindings=False),
            # dict(type="settings", custom_bindings=False)
            dict(type="settings", custom_bindings=True)
        ]

    def _gpio_board_to_bcm(self, pin):
        if gpiozero.pi_info().headers['J8'].rows == 20: # This is a 40 pin Pi
            pin_to_gpio = self._pin_to_gpio_rev3
        else: # This is a 26 pin Pi
            pin_to_gpio = self._pin_to_gpio_rev2
            
        return pin_to_gpio[pin]

    def _gpio_bcm_to_board(self, pin):
        if gpiozero.pi_info().headers['J8'].rows == 20: # This is a 40 pin Pi
            pin_to_gpio = self._pin_to_gpio_rev3
        else: # This is a 26 pin Pi
            pin_to_gpio = self._pin_to_gpio_rev2

        return pin_to_gpio.index(pin)

    # def _gpio_get_pin(self, pin):
        # if (GPIO.getmode() == GPIO.BOARD and self.GPIOMode == 'BOARD') or (GPIO.getmode() == GPIO.BCM and self.GPIOMode == 'BCM'):
            # return pin
        # elif GPIO.getmode() == GPIO.BOARD and self.GPIOMode == 'BCM':
            # return self._gpio_bcm_to_board(pin)
        # elif GPIO.getmode() == GPIO.BCM and self.GPIOMode == 'BOARD':
            # return self._gpio_board_to_bcm(pin)
        # else:
            # return 0

    # def _configure_gpio(self):

        # self._logger.info('\n{0:color}'.format(gpiozero.pi_info().headers['J8']))
        # self._logger.info("GPIO is in %s mode" % self.GPIOMode)
         
        # for button in self._configuredButton:
            # self._logger.debug("Cleaning up button %s" % button)
            # try:
                # button.close()
            # except (RuntimeError, ValueError) as e:
                # self._logger.error(e)
        # self._configuredButton = []

        # for pin in self._settingsGPIOPins:
            # self._configure_gpio_pin(pin);
        
    # def _configure_gpio_pin(self,pin):
        # self._logger.info("Configuring GPIO for pin %s" % pin)
        # try:
            # button = Button(self._gpio_board_to_bcm(pin),hold_time=0.1)
            # if pin == self.PSUButtonGPIOPin:
                # button.when_held = self._toggle_psu
            # elif pin == self.startButtonGPIOPin:
              # button.when_pressed = self._printer.start_print
                # button.when_pressed = self._toggle_psu
            # elif pin == self.pauseButtonGPIOPin:
               # button.when_pressed = self._toggle_pause
                # button.when_pressed = self._toggle_psu
            # elif pin == self.stopButtonGPIOPin:
                # button.when_held = self._stop_print
            # elif pin == self.XAddButtonGPIOPin:
                # button.when_pressed = self._jog
            # elif pin == self.XSubButtonGPIOPin:
                # button.when_pressed = self._jog
            # elif pin == self.YAddButtonGPIOPin:
                # button.when_pressed = self._jog
            # elif pin == self.YSubButtonGPIOPin:
                # button.when_pressed = self._jog
            # elif pin == self.ZAddButtonGPIOPin:
                # button.when_pressed = self._jog
            # elif pin == self.ZSubButtonGPIOPin:
                # button.when_pressed = self._jog
            # elif pin == self.XYHomeButtonGPIOPin:
                # button.when_pressed = self._home
            # elif pin == self.ZHomeButtonGPIOPin:
                # button.when_pressed = self._home
                
            # self._configuredButton.append(button)
            
        # except (RuntimeError, ValueError) as e:
            # self._logger.error(e)

    def _toggle_psu(self,button):
        pressPin = self._gpio_bcm_to_board(button.pin.number)
        if not self.get_psu_state():
            self._logger.info('Will turn PSU on!')
            self.turn_psu_on()
        elif self._printer.is_printing() or self._printer.is_paused():
            timer = 5
            while (timer > 0 and button.is_held):
                self._logger.info("Toggle Printer OFF in " + str(timer) + " seconds")
                timer -=1
                time.sleep(1)
            if (timer == 0):
                self._logger.info('Will turn PSU off!')
                self.turn_psu_off()
            else:
                self._logger.info("Toggle Printer OFF aborted")
        else:
            self._logger.info('Will turn PSU off!')
            self.turn_psu_off()

    def _toggle_pause(self):
        self._logger.info(self._printer.is_paused())
        if self._printer.is_paused():
            self._logger.info("Resume print")
            self._printer.toggle_pause_print()
        elif self._printer.is_printing():
            self._logger.info("Pause print")
            self._printer.toggle_pause_print()

    def _stop_print(self,button):
        if self._printer.is_printing() or self._printer.is_paused():
            timer = 5
            while (timer > 0 and button.is_held):
                self._logger.info("Stopping Printer in " + str(timer) + " seconds")
                timer -=1
                time.sleep(1)
            if (timer == 0):
                self._logger.info("Stop print")
                self._printer.cancel_print()
            else:
                self._logger.info("Stop printer aborted")

    def _action(self,button):
        return 
        
    def _gcode(self,button):
        return 
        
    def _home(self,button):
        pressPin = self._gpio_bcm_to_board(button.pin.number)
        self._logger.info(self.button_definitions[pressPin]['axis'])
        if self.button_definitions[pressPin]['axis'] == "Z":
            self._logger.info("Homing Z")
#            self._printer.home("z")
        elif self.button_definitions[pressPin]['axis'] == "XY":
            self._logger.info("Homing XY")
#            self._printer.home("x")
#            self._printer.home("y")
            
    def _jog(self,button):
        pressPin = self._gpio_bcm_to_board(button.pin.number)
        self._logger.info(self.button_definitions[pressPin]['axis'])
        self._logger.info(self.button_definitions[pressPin]['dist'])
#            self._printer.jog(dict(self.button_definitions[pressPin]['axis']=self.button_definitions[pressPin]['dist']))
        
    def test_callback(self,pin):
        self._logger.info('This is a edge event callback function!')
        self._logger.info('Edge detected on channel %s'%pin)
        self._logger.info('This is run in a different thread to your main program')
        
	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/OctoButtons.js"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			OctoButtons=dict(
				displayName="OctoButtons",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="DreadPirateMiko",
				repo="OctoPrint-OctoButtons",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/DreadPirateMiko/OctoPrint-OctoButtons/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "OctoButtons"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OctoButtons()

	# global __plugin_helpers__
	# __plugin_helpers__ = dict(
		# version_checks=version_checks,
		# updaters=updaters,
		# exceptions=exceptions,
		# util=util
	# )

	global __plugin_hooks__
#	__plugin_hooks__ = {
#		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
#	}