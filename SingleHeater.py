from ..Script import Script
from SingleHeaterImpl import SingleHeaterImpl


class SingleHeater(Script, SingleHeaterImpl):
    def getSettingDataString(self):
        return """{
            "name": "Single heater",
            "key": "SingleHeater",
            "metadata": {},
            "version": 2,
            "settings":
            {
            }
        }"""

    def load_parameters(self):
        pass
        
    def execute(self, data: list):
        """data is a list. Each index contains a layer"""
        self.load_parameters()

        zero_temp = False

        for index, layer in enumerate(data):
            lines = layer.split("\n")
            new_layer, zero_temp_inserted = self.processLayer(lines)
            data[index] = '\n'.join(new_layer)
            zero_temp = zero_temp or zero_temp_inserted

        if not zero_temp:
            # this shoudn't happened, just in case
            data[index] += '\n; WARNING resert temeperature missing\nM104 S0'
        return data
