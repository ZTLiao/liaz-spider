class CosConfig:
    def __init__(self, secret_id, secret_key, bucket_name, region):
        print('secret_id : ', secret_id, ', secret_key : ', secret_key, ', bucket_name : ', bucket_name, ', region : ', region)
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.region = region
