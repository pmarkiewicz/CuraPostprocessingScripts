from ..Script import Script


MESSAGE = """;TYPE:CUSTOM
;added code by post processing
;script: SimplePauseAtLayer.py action no:
;layer: {0} cmd: {1}\n
"""


class SimplePauseAtLayer(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Simple pause At Layer",
            "key": "PauseAtLayer",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "g_code":
                {
                    "label": "g-code",
                    "description": "g-code to pause",
                    "type": "str",
                    "default_value": "M226"
                },
                "layer_no":
                {
                    "label": "Layer no",
                    "description": "Layer no to insert g-code",
                    "type": "int",
                    "default_value": 1
                }
            }
        }"""

    def execute(self, data: list):
        """data is a list. Each index contains a layer"""

        g_code = self.getSettingValueByKey("g_code")
        layer_no = self.getSettingValueByKey("layer_no")

        for index, layer in enumerate(data):
            lines = layer.split("\n")
            for line in lines:
                if not line.startswith(";LAYER:"):
                    continue

                try:
                    curr_layer_no = int(line[len(";LAYER:"):])
                except ValueError:
                    # Couldn't cast to int. Something is wrong with this g-code data.
                    continue

                if layer_no == curr_layer_no:
                    prepend_gcode = MESSAGE.format(layer_no, g_code)
                    prepend_gcode += g_code + "\n"

                    layer = prepend_gcode + layer

                    # Override the data of this layer with the
                    # modified data
                    data[index] = layer

                    break

        return data
