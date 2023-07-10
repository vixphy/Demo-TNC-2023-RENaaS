import json
from subprocess import call

def get_config_dict(router,tunnels):
    return {
        'router_number': router.number,
        'router_type': router.router_type,
        'public_ipv4': router.ipv4,
        'tunnels_config' : tunnels
    }

def install_freertr(router_list):
    def remote_install(router_config):
        user = 'admin'
        cmd = f"scp -o StrictHostKeyChecking=no -o CheckHostIP=no ./install.sh {user}@{router_config['public_ipv4']}:/home/{user}/"
       
        print(cmd)
        call(cmd.split(" "))   
        cmd = f"ssh -o StrictHostKeyChecking=no -o CheckHostIP=no {user}@{router_config['public_ipv4']} sudo bash install.sh"
      
        print(cmd)
        call(cmd.split(" "))
    import multiprocessing
    jobs = []
    for router_config in router_list:
        p = multiprocessing.Process(target=remote_install,args=[router_config])
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()        

def deploy_scp(router_list):
    for router_config in router_list:
        router_json_filename = f"./files/router.json"
        with open(router_json_filename, 'w', encoding='utf-8') as f:
            json.dump(router_config, f,ensure_ascii=False, indent=4)

        user = 'admin'
        cmd = f"scp -o StrictHostKeyChecking=no -o CheckHostIP=no {router_json_filename} {user}@{router_config['public_ipv4']}:/home/{user}"
      
        print(cmd)
        call(cmd.split(" "))
        cmd = f"scp -o StrictHostKeyChecking=no -o CheckHostIP=no freertr.py {user}@{router_config['public_ipv4']}:/home/{user}"
    
        print(cmd)
        call(cmd.split(" "))        
        cmd = f"scp -o StrictHostKeyChecking=no -o CheckHostIP=no config_templates.py {user}@{router_config['public_ipv4']}:/home/{user}"
    
        print(cmd)
        call(cmd.split(" "))
        

def execute_scp(router_list):
    for router_config in router_list:
        user = 'admin'
        cmd = f"ssh -o StrictHostKeyChecking=no -o CheckHostIP=no {user}@{router_config['public_ipv4']} sudo python3 freertr.py"
     
        print(cmd)
        call(cmd.split(" "))
        
def test_deploy(router_list):
    for router_config in router_list:
        router_json_filename = f"./files/router_{router_config['router_number']}.json"
        print(router_json_filename)
        with open(router_json_filename, 'w', encoding='utf-8') as f:
            json.dump(router_config, f,ensure_ascii=False, indent=4)
       