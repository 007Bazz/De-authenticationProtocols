import uuid
from hashlib import sha512

class UUIDSHA512:
    def __init__(self):
        pass

    def ap_start(self):
        """Generate initial data for AP. Will be passed to assoc_client later as ap_data"""
        #This is the master key to deassoc all clients if the ap goes down
        id = uuid.uuid4().hex
        hash = sha512(id.encode('utf-8')).hexdigest()
        return {"id": id, "hash": hash}

    def ap_assoc(self, ap_data, body):
        if not "hash" in body:
            return (False)
        id = uuid.uuid4().hex
        hash = sha512(id.encode('utf-8')).hexdigest()
        return (True, {"client_hash": body["hash"], "ap_id": id}, {"hashes": [hash, ap_data["hash"]]})
    
    def ap_verify_deauth(self, ap_data, client_data, body):
        if not "id" in body:
            return False
        if not sha512(body["id"].encode('utf-8')).hexdigest() == client_data["client_hash"]:
            return False
        return True
    
    def ap_deauth_client(self, ap_data, client_data):
        return {"id": client_data["ap_id"]}
    
    def ap_deauth_all(self, ap_data):
        return {"id": ap_data["id"]}
    
    def client_assoc(self):
        id = uuid.uuid4().hex
        hash = sha512(id.encode('utf-8')).hexdigest()
        return ({"id": id}, {"hash": hash})
    
    def client_verify_deauth(self, ap_data, body):
        if not "id" in body:
            return False
        hash = sha512(body["id"].encode('utf-8')).hexdigest()
        if hash in ap_data["hashes"]:
            return True
        return False

