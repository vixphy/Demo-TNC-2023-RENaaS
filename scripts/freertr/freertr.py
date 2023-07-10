import uuid
from random import randint
try:
    from .config_templates import initial_config,final_config,backbone_protocols,vrf_definitions
    from .config_templates import default_interfaces,monitoring_tunnel_template,vxlan_tunnel_template,tunnel_template,hw_template
except:
    from config_templates import initial_config,final_config,backbone_protocols,vrf_definitions
    from config_templates import default_interfaces,monitoring_tunnel_template,vxlan_tunnel_template,tunnel_template,hw_template

def get_tunnel_vxlan_config(router1,router2):
    tunnel_name_template = 'tunnel{src}{dst}'
    description_template = "router {src} -> router {dst}"
    tunnel_key = '1234'
    tunnel_mode = 'vxlan'
    tunnel_vrf_forward = 'vxlan'
    tunnel_ipv4_template = '124.0.{number}.{index}'
    tunnel_mask = '255.255.240.0'
    n1,n2 = min(router1.number,router2.number), max(router1.number,router2.number)
    tunnel1 = {
        "tunnel_name":tunnel_name_template.format(src=router1.number,dst=router2.number),
        "description":description_template.format(src=router1.number,dst=router2.number),
        "tunnel_key":tunnel_key,
        "destination_ip": router2.ipv4,
        "tunnel_mode":tunnel_mode,
        "tunnel_vrf_forward":tunnel_vrf_forward,
        "tunnel_ipv4": tunnel_ipv4_template.format(number=f'{n1}{n2}' ,index=1 if router1.number>router2.number else 2),
        "tunnel_mask":tunnel_mask,
          
    }
    tunnel2 = {
        "tunnel_name":tunnel_name_template.format(src=router2.number,dst=router1.number),
        "description":description_template.format(src=router2.number,dst=router1.number),
        "tunnel_key":tunnel_key,
        "destination_ip": router1.ipv4,
        "tunnel_mode":tunnel_mode,
        "tunnel_vrf_forward":tunnel_vrf_forward,
        "tunnel_ipv4": tunnel_ipv4_template.format(number=f'{n1}{n2}',index=1 if router2.number>router1.number else 2),
        "tunnel_mask":tunnel_mask,
           
        }
    router1.n_tunnels +=1
    router2.n_tunnels +=1

    return tunnel1,tunnel2


class FreeRTR:
    def __init__(self,router_number,router_type,public_ipv4,tunnels_config=None,vm=None,interface_mac = None):
        self.number = router_number
        self.router_type = router_type
        self.ipv4 = public_ipv4
        if interface_mac is None:
            # self.interface_mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
            self.interface_mac = '\{placeholder_for_mac\}'
        else:
            self.interface_mac = interface_mac
        self.hostname= f"{router_type}{router_number}"
        self.description= "text to inform everything we need about the router"
        self.sw_file = '/rtr/rtr-sw.txt'.format(number=router_number)
    
        self.hw_file = '/rtr/rtr-hw.txt'.format(number=router_number)
  
        self.tunnels_config=tunnels_config
        self.tunnels = []
        self.n_tunnels = 0

    def add_vxlan_tunnel(self,destination_ip,dst_router,tunnel_number,tunnel_ipv4 = None):
        tunnel_number = len(self.tunnels) +1
        tunnel_ipv4_template = "{tunnel_number}0.{tunnel_number}0.{tunnel_number}0.{src}"
        tunnel_ipv6_template = "{tunnel_number}0{tunnel_number}0::{src} ffff::"
        var_description_template = "{router_type}{src} -> {router_type}{dst}"
        description=var_description_template.format(router_type=self.router_type,src=self.number,dst=dst_router)
        self.tunnels.append(
            vxlan_tunnel_template.format(
                number=tunnel_number,
                description = description,
                destination_ip=destination_ip,
                tunnel_ipv4=tunnel_ipv4_template.format(tunnel_number=tunnel_number,src=self.number),
                tunnel_ipv6=tunnel_ipv6_template.format(tunnel_number=tunnel_number,src=self.number)            
            )
        )

    def add_generated_tunnel(self,tunnel):
        self.tunnels.append(tunnel_template.format(**tunnel))

    def add_monitoring_tunnel(self,destination_ip,tunnel_ipv4 = None):
        tunnel_number = 0
        var_description_template = "{router_type}{src}"
        tunnel_key = 51820
        if tunnel_ipv4 is None:
            tunnel_ipv4 = f"10.0.0.{self.number+1}"
        description="monitoring router: "+ var_description_template.format(router_type=self.router_type,src=self.number)
        self.tunnels.append(
            monitoring_tunnel_template.format(
                number=tunnel_number,
                tunnel_key=tunnel_key,
                description = description,
                destination_ip=destination_ip,
                tunnel_ipv4=tunnel_ipv4          
            )
        )
        
    def write_sw_config(self):
        opened_sw_file = open(self.sw_file,'r+')
        string_list = opened_sw_file.readlines()
        string_list[0]=f'hostname {self.hostname}\n'
        initial_config = "".join(string_list[:80])
        with open(self.sw_file,'w') as f:
            f.write(initial_config)
            f.write(vrf_definitions)
            f.write(backbone_protocols)
            f.write(default_interfaces)
            for tunnel in self.tunnels:
                f.write(tunnel)
            f.write(final_config)

    def write_hw_config(self):
        hundred = (self.number-1)*100        
        port1,port2 = 20002+hundred,20001+hundred
        port3,port4 = 20012+hundred,20011+hundred
        port5,port6 = 20022+hundred,20021+hundred
        hw_content = hw_template.format(hostname=self.hostname,
                                        interface_mac=self.interface_mac,
                                        port1=port1,port2=port2,
                                        port3=port3,port4=port4,
                                        port5=port5,port6=port6
                                        )
        with open(self.hw_file, "w") as f:
            f.write(hw_content)

    def generate_from_config(self):
        import re
        for index,tunnel_config in enumerate(self.tunnels_config):
            if re.search('monitoring',tunnel_config.get('tunnel_vrf_forward','')):
                self.add_monitoring_tunnel(tunnel_config['destination_ip'])
            elif re.search('vxlan',tunnel_config.get('tunnel_vrf_forward','')):
                self.add_generated_tunnel(tunnel=tunnel_config)
     
        self.write_sw_config()
        self.write_hw_config()

if __name__ == "__main__":
    import json
    import netifaces
    with open('router.json') as json_file:
        config = json.load(json_file)
    
    interface_mac = netifaces.ifaddresses('enX0')[netifaces.AF_LINK][0]['addr']
    router = FreeRTR(**config,interface_mac=interface_mac)
    router.generate_from_config()