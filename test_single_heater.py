import unittest
from SingleHeaterImpl import SingleHeaterImpl


class TestSingleHeater(unittest.TestCase):
    def setUp(self):
        self.single_heater = SingleHeaterImpl()

    def test_temperature(self):
        values = [('M104 S100', 100), ('M109 T1 S99', 99), ('M104 T0 S0', 0)]

        for val in values:
            self.assertEqual(self.single_heater.getTemperature(val[0]), val[1])

    def test_process_temperature_pre(self):
        values = [
            (['M104 S151'], ['M104 S151']),
            (['M104 S150', 'M104 T1 S0'], ['M104 S150']),
            (['M109 T0 S0', 'M109 T1 S100'], ['M109 S100']),
            (['M104 S152', 'M109 S140'], ['M104 S152', 'M109 S140']),
            (['M104 S153', 'M104 S15', 'M104 S1', 'M109 S140'], ['M104 S153', 'M109 S140']),
            (['M104 S154', 'M109 S140', 'M104 S130'], ['M104 S154', 'M109 S140', 'M104 S130']),
            (['M104 S15', 'M104 S15', 'M104 S199', 'M109 S140', 'M109 S140'], 
             ['M104 S199', 'M109 S140']),
            (['M104 S0'], []),
            (['M104 S0', 'M109 S0'], []),
        ]

        for val in values:
            result = self.single_heater.processTemperatures(val[0], False)
            self.assertEqual(val[1], result)

    def test_process_temperature_layer(self):
        values = [
            (['M104 S151'], ['M104 S151']),
            (['M104 S0', 'M104 T1 S150'], ['M104 S150']),
            (['M109 T0 S0', 'M109 T1 S100'], ['M104 S100']),
            (['M104 S152', 'M109 S140'], ['M104 S152']),
            (['M104 S152', 'M109 S160'], ['M104 S160']),
            (['M104 S153', 'M104 S15', 'M104 S1', 'M109 S140'], ['M104 S153']),
            (['M104 S154', 'M109 S140', 'M104 S130'], ['M104 S154']),
            (['M104 S15', 'M104 S15', 'M104 S199', 'M109 S140', 'M109 S140'], ['M104 S199']),
            (['M104 S0'], []),
            (['M104 S0', 'M109 S0'], []),
            (['M109 S245', 'M104 T0 S0'], ['M104 S245']),
        ]

        for val in values:
            result = self.single_heater.processTemperatures(val[0], True)
            self.assertEqual(val[1], result)

    def test_file_prolog(self):
        data = """
;FLAVOR:RepRap
;TIME:1827
;Filament used: 0.0257679m, 2.16741m
;Layer height: 0.2
;Generated with Cura_SteamEngine 3.6.0
T0
M190 S70
M104 S245
M104 T1 S120
M109 S245
M109 T1 S120
M82 ;absolute extrusion mode
;M42  ; enable 2nd fan
G28 X;Home
G28 Y;Home
"""
        expected = """
;FLAVOR:RepRap
;TIME:1827
;Filament used: 0.0257679m, 2.16741m
;Layer height: 0.2
;Generated with Cura_SteamEngine 3.6.0
T0
M190 S70
; M104 S245
; M104 T1 S120
; M109 S245
; M109 T1 S120
M104 S245
M109 S245
M82 ;absolute extrusion mode
;M42  ; enable 2nd fan
G28 X;Home
G28 Y;Home
"""
        result, zero_temp = self.single_heater.processLayer(data.split('\n'))
        print(result)
        self.assertFalse(zero_temp)
        self.assertEqual(expected.split('\n'), result)

    def test_gcode(self):
        data = """
;LAYER:0
M107
G1 X20.945 Y109.239 E0.02416
G0 F1620 X20.97 Y109.23
G0 X21.464 Y109.122
G1 F1200 E-16
T1
M109 S245
M104 T0 S0
;MESH:corexy test v3 v1.stl
G0 F3600 X21.464 Y109.122 Z0.3
G1 F3000 E-2
G0 F3600 X21.464 Y119.122
G0 X17.789 Y115.449
G0 X18.019 Y109.371
;TYPE:SKIRT
G1 F3000 E2"""

        expected = """
;LAYER:0
M107
G1 X20.945 Y109.239 E0.02416
G0 F1620 X20.97 Y109.23
G0 X21.464 Y109.122
G1 F1200 E-16
T1
; M109 S245
; M104 T0 S0
M104 S245
;MESH:corexy test v3 v1.stl
G0 F3600 X21.464 Y109.122 Z0.3
G1 F3000 E-2
G0 F3600 X21.464 Y119.122
G0 X17.789 Y115.449
G0 X18.019 Y109.371
;TYPE:SKIRT
G1 F3000 E2"""
        result, zero_temp = self.single_heater.processLayer(data.split('\n'))
        print(result)
        self.assertFalse(zero_temp)
        self.assertEqual(expected.split('\n'), result)

    def test_zero_temp(self):
        data = """
;LAYER:0
M107
G1 X20.945 Y109.239 E0.02416
G0 F1620 X20.97 Y109.23
G0 X21.464 Y109.122
G1 F1200 E-16
T1
M109 S245
M104 T0 S0
;MESH:corexy test v3 v1.stl
G0 F3600 X21.464 Y109.122 Z0.3
G1 F3000 E-2
G0 F3600 X21.464 Y119.122
G0 X17.789 Y115.449
G0 X18.019 Y109.371
;TYPE:SKIRT
G1 F3000 E2
M104 S0
M109 S0
;End of Gcode"""

        expected = """
;LAYER:0
M107
G1 X20.945 Y109.239 E0.02416
G0 F1620 X20.97 Y109.23
G0 X21.464 Y109.122
G1 F1200 E-16
T1
; M109 S245
; M104 T0 S0
M104 S245
;MESH:corexy test v3 v1.stl
G0 F3600 X21.464 Y109.122 Z0.3
G1 F3000 E-2
G0 F3600 X21.464 Y119.122
G0 X17.789 Y115.449
G0 X18.019 Y109.371
;TYPE:SKIRT
G1 F3000 E2
; M104 S0
; M109 S0
M104 S0
;End of Gcode"""
        result, zero_temp = self.single_heater.processLayer(data.split('\n'))
        print(result)
        self.assertTrue(zero_temp)
        self.assertEqual(expected.split('\n'), result)







