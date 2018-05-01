from ..Script import Script


MESSAGE = """;TYPE:CUSTOM
;added code by post processing
;script: OnLayerChange.py action no: {0}
"""


class OnLayerChange(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "On layer change",
            "key": "OnLayerChange",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "action":
                {
                    "label": "Action",
                    "description": "Action on layer change. Separate by | to alternate layers. Use {} to insert layer no",
                    "type": "str",
                    "default_value": ""
                }
            }
        }"""

    def execute(self, data: list):
        """data is a list. Each index contains a layer"""

        action = self.getSettingValueByKey("action").split("|")
        no_of_actions = len(action)

        for index, layer in enumerate(data):
            lines = layer.split("\n")
            for line in lines:
                if not line.startswith(";LAYER:"):
                    continue

                try:
                    layer_no = int(line[len(";LAYER:"):])
                except ValueError:    
                    # Couldn't cast to int. Something is wrong with this g-code data.
                    continue

                action_no = layer_no % no_of_actions
                prepend_gcode = MESSAGE.format(action_no)
                prepend_gcode += action[action_no].format(layer_no) + "\n"

                layer = prepend_gcode + layer

                # Override the data of this layer with the
                # modified data
                data[index] = layer

        return data
