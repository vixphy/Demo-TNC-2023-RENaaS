from freertr import FreeRTR,get_tunnel_vxlan_config
from utils import *

if __name__ == "__main__":
    monitoring_ipv4 = '35.x.x.x'
    r1 = FreeRTR(1,'r',"10.x.x.x")
    r2 = FreeRTR(2,'r',"10.x.x.x")
    r1tunnel,r2tunnel = get_tunnel_vxlan_config(r1,r2)
    r1_config = get_config_dict(r1,
        tunnels=[
            r1tunnel,
            {
                'tunnel_vrf_forward':'monitoring',
                'destination_ip':monitoring_ipv4
            },
        ])
    r2_config = get_config_dict(r2,
        tunnels=[           
           r2tunnel,  
            {
                'tunnel_vrf_forward':'monitoring',
                'destination_ip':monitoring_ipv4
            },
        ])
    router_list = [r1_config,r2_config]
    install_freertr(router_list)
    deploy_scp(router_list)
    execute_scp(router_list)
