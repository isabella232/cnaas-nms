from nornir import InitNornir

from nornir.core.deserializer.inventory import Inventory
from nornir.core.filter import F

from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_title, print_result

import cnaas_nms.confpush.nornir_helper
from cnaas_nms.cmdb.session import session_scope
from cnaas_nms.cmdb.device import Device
from cnaas_nms.scheduler.scheduler import Scheduler

import datetime

def push_base_management(task):
    template_vars = {
        'uplinks': [{'ifname': 'Ethernet2'}],
        'mgmt_vlan_id': 600,
        'mgmt_ip': '10.0.6.10/24',
        'mgmt_gw': '10.0.6.1'
    }
    print("DEBUG1: "+task.host.name)
    #TODO: find uplinks automatically
    #TODO: check compatability, same dist pair and same ports on dists
    #TODO: query mgmt vlan, ip, gw for dist pair

    r = task.run(task=text.template_file,
                 name="Base management",
                 template="managed-base.j2",
                 path=f"../templates/{task.host.platform}",
                 **template_vars)

    #TODO: Handle template not found, variables not defined

    task.host["config"] = r.result

    task.run(task=networking.napalm_configure,
             name="Push base management config",
             replace=False,
             configuration=task.host["config"],
             dry_run=True # TODO: temp for testing
             )

def init_access_device(hostname=None):
    """Initialize access device for management by CNaaS-NMS

    Args:
        hostname (str): Hostname of device to initialize

    Returns:
        Nornir result object
    """
    #TODO: step1. update device state

    # step2. push management config
#    nr = cnaas_nms.confpush.nornir_helper.cnaas_init()
#    nr_filtered = nr.filter(name=hostname)

#    result = nr_filtered.run(task=push_base_management)

#    print_result(result)
    # expect connection lost

    # step3. register apscheduler job that continues steps

    scheduler = Scheduler()
    job = scheduler.add_job(init_access_device_step2, trigger=None, id='1', kwargs={'hostname':'debug2'})
    print(f"Job ID {job.id} scheduled")

    # step4+ in apjob: if success, update management ip and device state, trigger external stuff?

#    return result

def init_access_device_step2(hostname=None):
    print(f"step2: { hostname }")