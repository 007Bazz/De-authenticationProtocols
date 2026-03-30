class Normal:
    def __init__(self):
        pass

    def ap_start(self):
        return None

    def ap_assoc(self, ap_data, body):
        return (True, {}, {})
    
    def ap_verify_deauth(self, ap_data, client_data, body):
        return True
    
    def ap_deauth_client(self, ap_data, client_data):
        return {}
    
    def ap_deauth_all(self, ap_data):
        return {}
    
    def client_assoc(self):
        return ({},{})
    
    def client_verify_deauth(self, ap_data, body):
        return True
