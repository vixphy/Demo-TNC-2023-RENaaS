from freertr import FreeRTR
from utils import *

if __name__ == "__main__":
    remote_test = True

    r1 = FreeRTR(1,'r',"ip_vm")
    r2 = FreeRTR(2,'r',"ip_vm")
    

    r1_config = get_config_dict(r1,
        tunnels=[
            {
                'tunnel_id':'vxlan_1',
                'tunnel_number':1,
                'endpoint_ipv4':r2.ipv4,
                'endpoint_router':r2.number
            },
        ])
    
    r2_config = get_config_dict(r2,
        tunnels=[
            {
                'tunnel_id':'vxlan_2',
                'tunnel_number':2,
                'endpoint_ipv4':r1.ipv4,
                'endpoint_router':r1.number
            },
        ])
    
    router_list = [r1_config,r2_config]
    deploy_scp(router_list)
    execute_scp(router_list)
