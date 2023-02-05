from oslo_concurrency import processutils
from pathlib import Path
from collections import OrderedDict
import json
import sys
import os
import pandas as pd
(out, err) = processutils.execute('openstack', 'hypervisor', 'list', '--long', '-c', 'Hypervisor Hostname', '-c', 'State', '-c', 'vCPUs Used', '-c', 'vCPUs', '-c', 'Memory MB Used', '-c', 'Memory MB', '-f', 'json')
hypervisor_info = json.loads(out)
(out, err) = processutils.execute('openstack', 'host', 'list', '-f', 'json')
host_info = json.loads(out)
for hypervisor in hypervisor_info:
    hypervisor = OrderedDict(hypervisor)
    for host in host_info:
        if hypervisor.get('Hypervisor Hostname') == host.get('Host Name'):
            hypervisor['Zone'] = host.get('Zone')
    hypervisor.move_to_end('Zone', last=False)
    df = pd.DataFrame(hypervisor, index=[0])
    if not Path('hypervisor_usage.csv').exists():
        df.to_csv('hypervisor_usage.csv', header=True, index=False)
    else:
        df.to_csv('hypervisor_usage.csv', mode='a', header=False, index=False)
