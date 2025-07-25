# Filament Buffer Pressure Sensor
#
# Copyright (C) 2023-2025 JR Lomas (discord:knight_rad.iant) <lomas.jr@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import logging

class FPS:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name()
        self.printer.add_object(self.name, self)
        
        # state variables
        self.fps_value = 0.0
        
        self._pin = config.get('pin')
        self._sample_count = config.getint('sample_count', 5)
        self._sample_time = config.getfloat('sample_time', 0.005)
        self._report_time = config.getfloat('report_time', 0.100)
        self._reversed = config.getboolean('reversed', False)

        self._sf_max_speed = config.getfloat('max_speed', 300.0)
        self._accel = config.getfloat('accel', 0.0)
        self._set_point = config.getfloat('set_point', 0.5)
        
        self.extruder_name = config.get('extruder')
        
        self.oams_names = config.get('oams').split(',')
        self.oams = []
        for name in self.oams_names:
            oam = self.printer.lookup_object("oams " + name.strip())
            if oam is None:
                raise ValueError(f"Object '{name}' not found")
            self.oams.append(oam)
        
        # printer objects
        self.ppins = self.adc = None

        self.ppins = self.printer.lookup_object('pins')
        self.adc = self.ppins.setup_pin('adc', self._pin)
        self.use_kalico = config.getboolean('use_kalico', False)
        if self.use_kalico:
            self.adc.setup_minmax(self._sample_time, self._sample_count)
        else:
            self.adc.setup_adc_sample(self._sample_time, self._sample_count)
        self.adc.setup_adc_callback(self._report_time, self._adc_callback)
        
        self.callbacks = []
        
        # handle ready
        self.printer.register_event_handler("klippy:ready", self.on_ready)
        
    def on_ready(self):
        self.extruder = self.printer.lookup_object(self.extruder_name)
        if self.extruder is None:
            raise ValueError(f"Object '{self.extruder_name}' not found")
        
    def add_callback(self, callback):
        self.callbacks.append(callback)

    def _adc_callback(self, read_time, read_value):
        if self._reversed:
            read_value = 1.0 - read_value
        self.fps_value = read_value
        if self.callbacks:
            for callback in self.callbacks:
                callback(read_time, read_value)
        
    def get_status(self, eventtime):
        return {
            'fps_value': self.fps_value,
        }
    
    def get_value(self):
        return self.fps_value
            
def load_config_prefix(config):
    return FPS(config)