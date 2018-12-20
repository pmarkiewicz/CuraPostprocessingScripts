# CuraPostprocessingScripts

Additional post processing scripts for Cura.

Install
In Cura goto Help -> Show configuration folder and copy scripts to scripts folder.

OnLayerChange - actions for every layer, can be used to trigger camera to get better timelapse.

CoolBed - reduce bed temperature to target temperature by 1 deg

SingleHeater - workaround for configuration with many extruders and single heater.
This is currently (as Cura 3.6) unsupported configuration and creates a lot of mess while printing.
Postprocessor tries to merge different temperatures and skips every zero temperature. It inserts zero temperatura at the end of gcode.
