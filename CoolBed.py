from ..Script import Script

MESSAGE = """;TYPE:CUSTOM
;added code by post processing
;script: CoolBed.py
;DBG: curr temp={0}, start temp={1}, end temp={4}, tot layers: {2}, start layer: {3}
"""

LAYER_COUNT = ";LAYER_COUNT:"
LAYER = ";LAYER:"


class CoolBed(Script):
    def __init__(self):
        super().__init__()

        self.temp_step = 1.0
        self.desired_temperature = 0.0
        self.no_of_layers = 0
        self.start_layer = 0
        self.is_percent = False
        self.end_temperature = 0
        self.start_temperature = 0.0
        self.step_layer = 0
        self.requested_temperature = 0

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
                    "description": "Final temperature, or if negative difference to initial temperature",
                    "type": "float",
                    "default_value": 0
                }
            }
        }"""

    def calc_layer_step(self):
        dl = self.no_of_layers - self.start_layer
        dt = self.start_temperature - self.end_temperature

        # change by 1deg every x layers
        self.step_layer = int(dl / dt)

    def load_parameters(self):
        self.start_layer = self.getSettingValueByKey("start")
        self.is_percent = self.getSettingValueByKey("percent")
        self.requested_temperature = self.getSettingValueByKey("temperature")
        if self.requested_temperature > 0:
            self.end_temperature = self.requested_temperature

    def on_layer_count(self, line):
        # this is called only once
        try:
            self.no_of_layers = int(line[len(LAYER_COUNT):])
        except ValueError:
            # Couldn't cast to int. Something is wrong with this g-code data.
            return

        if self.is_percent:
            if self.start_layer <= 0 or self.start_layer >= 100:
                return

            percent = self.start_layer / 100.0
            self.start_layer = int(self.no_of_layers * percent)

        self.calc_layer_step()

    def on_bed_temperature_set(self, line):
        # M140 S60
        pos = line.index('S')
        try:
            self.start_temperature = float(line[pos+1:])
        except ValueError:
            return

        if self.requested_temperature < 0:
            self.end_temperature = self.start_temperature + self.requested_temperature

        self.desired_temperature = self.start_temperature
        self.calc_layer_step()

    def on_layer(self, line):
        try:
            layer_no = int(line[len(LAYER):])
        except ValueError:
            return None

        if (self.step_layer == 0
                or layer_no < self.start_layer
                or self.desired_temperature <= self.end_temperature
                or layer_no % self.step_layer != 0):
            return None

        self.desired_temperature -= self.temp_step
        return 'M140 S{}'.format(self.desired_temperature)

    def execute(self, data: list):
        """data is a list. Each index contains a layer"""
        self.load_parameters()

        for index, layer in enumerate(data):
            lines = layer.split("\n")
            for line in lines:
                if line.startswith(LAYER_COUNT):
                    self.on_layer_count(line)

                elif line.startswith("M190") or line.startswith("M140"):
                    self.on_bed_temperature_set(line)

                elif line.startswith(LAYER):
                    action = self.on_layer(line)

                    if action:
                        prepend_gcode = MESSAGE.format(self.desired_temperature,
                                                       self.start_temperature,
                                                       self.no_of_layers,
                                                       self.start_layer,
                                                       self.end_temperature)
                        prepend_gcode += action + "\n"

                        # Override the data of this layer with the modified data
                        data[index] = prepend_gcode + layer
        return data
