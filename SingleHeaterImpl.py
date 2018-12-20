import re

MESSAGE = """;TYPE:CUSTOM
;added code by post processing
;script: SingleHeater.py
"""

LAYER = ';LAYER:'
END_OF_CODE = ';End of Gcode'


class SingleHeaterImpl:
    def __init__(self):
        super().__init__()

        self.hotend_re = re.compile(r'M10[49]')
        self.temperature_re = re.compile(r'S(\d+)')

    def getTemperature(self, line):
        # only int temperatures
        match = self.temperature_re.search(line)
        if not match:
            raise RuntimeWarning('No temperature passed')

        temp = match.group(1)
        return int(temp)

    def processTemperatures(self, lines, regular_layer):
        """
        When source is
          
        M104 T1 S200
        M109 S150
        M109 T1 S200

        should be replaced by if before layers
        M104 S200
        M109 S200

        all codes with temperature equal to zero are skipped
        """
        result = []
        max_temp = 0

        item = lines.pop(0)
        max_temp = self.getTemperature(item)

        for line in lines:
            if regular_layer or item[0:4] == line[0:4]:  # continuation of same cmd
                temp = self.getTemperature(line)
                if temp > max_temp:
                    max_temp = temp
            else:                       # new command
                if max_temp > 0:                
                    result.append('{0} S{1}'.format(item[0:4], max_temp))

                item = line
                max_temp = self.getTemperature(item)

        if max_temp > 0:                
            if regular_layer:
                result.append('M104 S{0}'.format(max_temp))
            else:
                result.append('{0} S{1}'.format(item[0:4], max_temp))

        return result

    def processLayer(self, lines):
        # because we ignore zero temperatures we have to insert M104 S0
        # after line
        # ;End of Gcode
        result = []
        temperature_set = []
        zero_temp = False
        regular_layer = False

        for line in lines:
            if line.find(LAYER) == 0:
                regular_layer = True
            
            if line.find(END_OF_CODE) == 0:
                zero_temp = True
                result.append('M104 S0')
                result.append(line)
            elif self.hotend_re.search(line):
                temperature_set.append(line)
                result.append('; {0}'.format(line))
            elif temperature_set and not self.hotend_re.search(line):
                result += self.processTemperatures(temperature_set, regular_layer)
                result.append(line)
                temperature_set = []
            else:
                result.append(line)

        return result, zero_temp


