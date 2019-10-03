from . import ScribeModuleBaseClass
from . lib.util import format_url

import re as _re
import sys


class Cpuinfo(ScribeModuleBaseClass):

    def __init__(self, input_dict=None, module_name=None, host_name=None,
                 input_type=None, scribe_uuid=None):
        ScribeModuleBaseClass.__init__(self, module_name=module_name,
                                       input_dict=input_dict,
                                       host_name=host_name,
                                       input_type=input_type,
                                       scribe_uuid=scribe_uuid)
        if input_dict:
            self.value = self._parse(input_dict)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def _parse(self, cpu_fullinput):
        output_data = {}
        split_lines = cpu_fullinput.get("lscpu").split('\n')
        if len(split_lines) <= 1:
            print("Error occured in processing CPU Info data")
            sys.exit(1)
        for x in range(len(split_lines)):
            # There are cases where the value has leading whitespaces
            # And also removing multiple whitespaces in general
            split_lines[x] = _re.sub(r":\s\s+", ": ", split_lines[x])
            split_lines[x] = _re.sub(r"\s\s+", "", split_lines[x])
            # Flags are a special case in lscpu where we want to
            # convert it to a list. We generate that here and
            # remove the old line
            if "Flags" in split_lines[x]:
                new_flags = split_lines[x].split(' ')
                new_flags.remove('Flags:')
                split_lines.remove(split_lines[x])
        if split_lines[0] != "" and len(split_lines) >= 2:
            # Dealing with keys having whitespaces
            split_lines[0] = split_lines[0].replace(' ', '_')
            if split_lines[0] not in output_data:
                output_data[split_lines[0]] = []
            current_dict = {}
            for s in split_lines[1:]:
                if ': ' in s:
                    key_val = s.split(': ', 1)
                else:
                    continue
                if len(key_val) <= 1:
                    key_val.append("None")
                current_dict[key_val[0].replace(' ', '_')] = key_val[1]
            # We update our dictionary with the created Flags list above
            current_dict.update({'Flags': new_flags})
            output_data[split_lines[0]].append(current_dict)
        return output_data
