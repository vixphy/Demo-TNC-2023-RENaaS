# Auto FreeRTR:

The following scripts generate the freertr configurations based on the configuration templates and desired functions.

## Usage:

To use these scripts, first set your freertr:
```
    r1 = FreeRTR(int_index_1,'r',public_ipv4_router1)
    r2 = FreeRTR(int_index_2,'r',public_ipv4_router2)
```

Then, configure  the tunnels:

```
r1_config = get_config_dict(r1,
        tunnels=[
            {
                'tunnel_id':'monitoring',
                'endpoint_ipv4':monitoring_ipv4
            },
            {
                'tunnel_id':'vxlan_1',
                'endpoint_ipv4':r2.ipv4,
                'endpoint_router':r2.number
            }
        ])
r2_config = get_config_dict(r2,
        tunnels=[
            {
                'tunnel_id':'monitoring',
                'endpoint_ipv4':monitoring_ipv4
            },
            {
                'tunnel_id':'vxlan_1',
                'endpoint_ipv4':r1.ipv4,
                'endpoint_router':r1.number
            }
        ])
router_list = [r1_config,r2_config]
```

## Deploying:

Make sure you have ssh access to all endpoints and  call the functions: 

`deploy_scp(router_list)` and `execute_scp(router_list)`. 

These functions copy the necessary files and generate the rtr-sw.txt and rtr-hw.txt on the desired path of the remote machine, which is by default '/rtr/rtr-sw.txt' and '/rtr/rtr-hw.txt'.
