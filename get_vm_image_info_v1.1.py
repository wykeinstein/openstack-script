from oslo_concurrency import processutils
from pathlib import Path
import json
import sys
import os
import pandas as pd
(out, err) = processutils.execute("openstack", "server", "list", '--all', "-c", "Name", "-c", "ID", "-f", "json")
all_vm_info = json.loads(out)
vm_dict_list = list()
for i in all_vm_info:
    (out, err) = processutils.execute("openstack", "server", "show", i['ID'], "-c", "volumes_attached", "-f", "json")
    vm_vol = json.loads(out)
    # 从镜像启动的虚拟机，其volumes_attached为空列表
    if vm_vol['volumes_attached'] == []:
        i['root_disk_id'] = ''
        (out, err) = processutils.execute("openstack", "server", "show", i['ID'], "-c", "image", "-f", "json")
        vm_image = json.loads(out)
        i['image'] = vm_image['image']
    # 从镜像卷或者卷启动的虚拟机
    else:
        i['root_disk_id'] = vm_vol['volumes_attached'][0]['id']
        (out, err) = processutils.execute("openstack", "volume", "show", i['root_disk_id'], "-c", "volume_image_metadata", "-f", "json", check_exit_code=[0,1])
        # 当out != ''时，说明是从镜像卷启动的虚拟机
        if out != '':
            vol_image_info = json.loads(out)
            i['image'] = vol_image_info['volume_image_metadata']['image_name']
        # 当out == ''时，说明是从普通的卷启动的虚拟机
        else:
            i['image'] = ''
    df = pd.DataFrame(i, index=[0])
    if not Path('vm_image_info.csv').exists():
        df.to_csv(r'vm_image_info.csv', index=False, header=False)
    else:
        df.to_csv (r'vm_image_info.csv', mode='a', index = False, header=True)
    print(i)
