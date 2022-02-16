#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      <AUTHOR>                                  <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.5 and
#  upwards.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
import datetime

from lib.model.smartplugin import *
from lib.item import Items

from .webif import WebInterface

import numpy as np
import scipy
import threading


# If a needed package is imported, which might be not installed in the Python environment,
# add it to a requirements.txt file within the plugin's directory


class AdvancedLighting(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """

    PLUGIN_VERSION = '1.0.0'    # (must match the version specified in plugin.yaml), use '1.0.0' for your initial plugin Release

    def __init__(self, sh):
        """
        Initalizes the plugin.

        If you need the sh object at all, use the method self.get_sh() to get it. There should be almost no need for
        a reference to the sh object any more.

        Plugins have to use the new way of getting parameter values:
        use the SmartPlugin method get_parameter_value(parameter_name). Anywhere within the Plugin you can get
        the configured (and checked) value for a parameter by calling self.get_parameter_value(parameter_name). It
        returns the value in the datatype that is defined in the metadata.
        """

        # Call init code of parent class (SmartPlugin)
        super().__init__()

        # get the parameters for the plugin (as defined in metadata plugin.yaml):
        # self.param1 = self.get_parameter_value('param1')

        # cycle time in seconds, only needed, if hardware/interface needs to be
        # polled for value changes by adding a scheduler entry in the run method of this plugin
        # (maybe you want to make it a plugin parameter?)
        self._cycle = 60

        # Initialization code goes here

        # On initialization error use:
        #   self._init_complete = False
        #   return

        return

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.debug("Run method called")
        # setup scheduler for device poll loop   (disable the following line, if you don't need to poll the device. Rember to comment the self_cycle statement in __init__ as well)
        self.scheduler_add('poll_device', self.poll_device, cycle=self._cycle)

        self.alive = True
        # if you need to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.debug("Stop method called")
        self.scheduler_remove('poll_device')
        self.alive = False

    def thread_function(self, item, time,color,brightness):
        while True:
            self.getHCL2(2200,6500,time,color,brightness)
            if(item.return_children())




    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference
        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.
        """

        if 'avl_times' in  item.conf:
            if not 'avl_brightness' in item.conf:
                self.logger.error('AdvancedLighting: avl_brightness not defined in item [{0}]'.format(item))
                return
            if not 'avl_color' in item.conf:
                self.logger.error('AdvancedLighting: avl_color not defined in item [{0}]'.format(item))
                return


            avl_times = str(item.conf['avl_times'])
            avl_brightness = item.conf['avl_brightness']
            avl_color = item.conf['avl_color']

            time = np.array([int(x) for x in avl_times.split(',')])*60*60
            brightness = np.array([int(x) for x in avl_brightness.split(',')])
            color = np.array([int(x) for x in avl_color.split(',')])

            x = threading.Thread(target=self.thread_function, args=(1,))
            x.start()


        if 'dpt3_dim_max' in item.conf:
            if not 'dpt3_dim_step' in item.conf:
                item.conf['dpt3_dim_step'] = '25'
                self.logger.warning('dimmenDPT3: no dpt3_dim_step defined in item [{0}] using default 25'.format(item))
            if not 'dpt3_dim_time' in item.conf:
                item.conf['dpt3_dim_time'] = '1'
                self.logger.warning('dimmenDPT3: no dpt3_dim_time defined in item [{0}] using default 1'.format(item))
            return self.dimDPT3

    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Item has been updated

        This method is called, if the value of an item has been updated by SmartHomeNG.
        It should write the changed value out to the device (hardware/interface) that
        is managed by this plugin.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        if self.alive and caller != self.get_shortname():
            # code to execute if the plugin is not stopped
            # and only, if the item has not been changed by this this plugin:
            self.logger.info("Update item: {}, item has been changed outside this plugin".format(item.id()))

            if self.has_iattr(item.conf, 'foo_itemtag'):
                self.logger.debug("update_item was called with item '{}' from caller '{}', source '{}' and dest '{}'".format(item,
                                                                                                               caller, source, dest))
            pass

    def poll_device(self):
        """
        Polls for updates of the device

        This method is only needed, if the device (hardware/interface) does not propagate
        changes on it's own, but has to be polled to get the actual status.
        It is called by the scheduler which is set within run() method.
        """
        # # get the value from the device
        # device_value = ...
        #
        # # find the item(s) to update:
        # for item in self.sh.find_items('...'):
        #
        #     # update the item by calling item(value, caller, source=None, dest=None)
        #     # - value and caller must be specified, source and dest are optional
        #     #
        #     # The simple case:
        #     item(device_value, self.get_shortname())
        #     # if the plugin is a gateway plugin which may receive updates from several external sources,
        #     # the source should be included when updating the the value:
        #     item(device_value, self.get_shortname(), source=device_source_id)
        pass

    def getHCL2(min_color, max_color, time, color, brightness):
        hour = 60 * 60
        current_time = datetime.datetime.now()

        # time = np.array([0, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]) * (60 * 60)
        # brightness = np.array([15, 15, 30, 100, 100, 100, 100, 80, 50, 30, 30, 15])
        # color = np.array([0, 0, 0, 45, 100, 100, 100, 50, 25, 0, 0, 0])

        brightness_f = scipy.interpolate.interp1d(time, brightness)
        # xnew = np.arange(0, 24 * hour, 0.1)
        # ynew = brightness_f(xnew)  # use interpolation function returned by `interp1d`
        # plt.plot(time / hour, brightness, 'o', xnew / hour, ynew, '-')
        # plt.show()

        color_f = scipy.interpolate.interp1d(time, color)
        # xnew = np.arange(0, 24 * hour, 0.1)
        # ynew = color_f(xnew)  # use interpolation function returned by `interp1d`
        # plt.plot(time / hour, color, 'o', xnew / hour, ynew, '-')
        # plt.show()

        color_range = max_color - min_color
        current_time = datetime.datetime.now()
        current_seconds = current_time.hour * 60 * 60 + current_time.minute * 60 + current_time.second
        target_brightness = brightness_f(current_seconds) + 0
        target_color = (color_f(current_seconds) * color_range) + min_color
        return (target_brightness, target_color)


    def dimDPT3(self, item: lib.item.item, caller=None, source=None, dest=None):
        # das ist die methode, die die DPT3 dimmnachrichten auf die dimmbaren items mapped
        # fallunterscheidung dimmen oder stop

        # auswertung der list werte für die KNX daten
        # [1] steht für das dimmen
        # [0] für die richtung
        # es wird die fading funtion verwendet
        valueMax = float(item.conf['dpt3_dim_max'])
        valueDimStep = float(item.conf['dpt3_dim_step'])
        valueDimTime = float(item.conf['dpt3_dim_time'])

        parent = item.return_parent()

        if item()[1] == 1:
            # dimmen
            if item()[0] == 1:
                # hoch
                parent.fade(valueMax, valueDimStep, valueDimTime)
            else:
                # runter
                parent.fade(0, valueDimStep, valueDimTime)
        else:
            # stoppe den fader
            parent._lock.acquire()
            parent._fading = False
            parent._lock.notify_all()
            parent._lock.release()


