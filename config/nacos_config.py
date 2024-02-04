import yaml

import system.global_vars
import nacos

profiles = {
    'DEV': {
        'username': 'nacos',
        'password': 'nacos',
        'serverAddr': '127.0.0.1:8848',
        'namespace': '5f49cd28-4eb2-4b0b-a467-bab25f4c9535',
        'sharedDataIds': 'application.yaml,database.yaml',
        'refreshableDataIds': 'application.yaml',
    },
    'TEST': {
        'username': 'nacos',
        'password': 'nacos',
        'serverAddr': '172.17.0.1:8848',
        'namespace': 'e85ee8e9-472c-4803-bcf0-0b0f7d0ea0b7',
        'sharedDataIds': 'application.yaml,database.yaml',
        'refreshableDataIds': 'application.yaml',
    },
    'PROD': {
        'username': 'nacos',
        'password': 'nacos',
        'serverAddr': '172.17.0.1:8848',
        'namespace': 'b8a5a983-8632-40f4-9e83-6783a4b1680c',
        'sharedDataIds': 'application.yaml,database.yaml',
        'refreshableDataIds': 'application.yaml',
    }
}


class NacosConfig:
    def __init__(self):
        try:
            env = system.global_vars.application.get_env()
            profile = profiles[env.upper()]
            self.server_addr = profile['serverAddr']
            self.namespace = profile['namespace']
            self.username = profile['username']
            self.password = profile['password']
            self.shared_data_ids = profile['sharedDataIds']
            client = nacos.NacosClient(self.server_addr, namespace=self.namespace, username=self.username, password=self.password)
            shared_data_id_array = self.shared_data_ids.split(',')
            self.yaml_conf = []
            for data_id in shared_data_id_array:
                config = yaml.load(client.get_config(data_id, 'DEFAULT_GROUP'), Loader=yaml.FullLoader)
                self.yaml_conf.append(config)
            print(self.yaml_conf)
        except Exception as e:
            print(e)


