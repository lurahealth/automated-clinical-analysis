Automated Clinical Analysis Tool

----------

Lura Health's First-In-Man Clinical Trial is supported by a "bluetooth mesh" network, 
where each patient pH sensor device can connect to any pH receiver module. This system
improves the rate of total connectivity events, but creates fragmented datasets.

This tool parses Lura Health's clinical server and pieces together fragments of pH sensor
data, by pH sensor device ID. Then, device ID datasets are analyzed for potential "red 
flags" such as improper pH readings, low battery level, etc. A summary of red flags, or
lack of red flags, can be emailed to individuals responsible for assessing device health 
throughout the duration of the study.
