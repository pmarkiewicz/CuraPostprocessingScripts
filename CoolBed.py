from ..Script import Script


MESSAGE = """;TYPE:CUSTOM
;added code by post processing
;script: CoolBed.py
;DBG: curr temp={0}, start temp={1}, tot layers: {2}
"""


class CoolBed(Script):
    def __init__(self):
        super().__init__()

        self.temp_step = 1.0
        self.no_of_layers = 0
        self.start_layer = 0
        self.is_percent = False
        self.end_temperature = 0
        self.start_temperature = 0
        self.current_temparature = 0
        self.step_layer = 0

    def getSettingDataString(self):
        return """{
            "name": "Cool bed",
            "key": "CoolBed",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "start":
                {
                    "label": "Start layer",
                    "description": "Layer to start decreasing temperature. Number to start at layer and append % to calculater proportional",
                    "type": "int",
                    "default_value": 0
                },
                "percent":
                {
                    "label": "Percent of height",
                    "description": "When enabled, it will start at percent of height.",
                    "type": "bool",
                    "default_value": false
                },
                "temperature":
                {
                    "label": "End temperature",
                    "description": "Final temperature",
                    "type": "int",
                    "default_value": 0
                }
            }
        }"""

    def calc_temp_step(self):
        dl = self.no_of_layers - self.start_layer
        dt = self.start_temperature - self.end_temperature

        # change by 1deg every x layers
        self.step_layer = int(dl / dt)

    def load_parameters(self):
        self.start_layer = self.getSettingValueByKey("start")
        self.is_percent = self.getSettingValueByKey("percent")
        self.end_temperature = self.getSettingValueByKey("temperature")

    def on_layer_count(self, line):
        try:
            self.no_of_layers = int(line[len(";LAYER_COUNT:"):])
        except ValueError:
            # Couldn't cast to int. Something is wrong with this g-code data.
            return

        if self.is_percent:
            percent = 1 / self.start_layer
            self.start_layer = int(self.no_of_layers * percent)

        self.calc_temp_step()

    def on_bed_temperature_set(self, line):
        pos = line.index('S')
        try:
            self.start_temperature = float(line[pos+1:])
        except ValueError:
            self.start_temperature = 999
            return

        self.calc_temp_step()

    def on_layer(self, line):
        try:
            layer_no = int(line[len(";LAYER:"):])
        except ValueError:
            # Couldn't cast to int. Something is wrong with this g-code data.
            return (False, '')

        if layer_no < self.start_layer :
            return (False, '')

        if self.step_layer != 0 and layer_no % self.step_layer == 0:
            self.current_temparature += self.temp_step
            return (True, 'M140 S{}'.format(self.start_temperature - self.current_temparature))

        return (False, '')


    def execute(self, data: list):
        """data is a list. Each index contains a layer"""
        self.load_parameters()

        for index, layer in enumerate(data):
            lines = layer.split("\n")
            for line in lines:
                if line.startswith(";LAYER_COUNT:"):
                    self.on_layer_count(line)
                    continue

                if line.startswith("M190") or line.startswith("M140"):
                    self.on_bed_temperature_set(line)

                if line.startswith(";LAYER:"):
                    insert, action = self.on_layer(line)

                    if insert:
                        prepend_gcode = MESSAGE.format(self.current_temparature, self.start_temperature, self.no_of_layers)
                        prepend_gcode += action + "\n"

                        layer = prepend_gcode + layer

                        # Override the data of this layer with the
                        # modified data
                        data[index] = layer
        return data