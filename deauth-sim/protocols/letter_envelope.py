import sympy

KEY_SIZE = 512

class LetterEnvelope:
    def __init__(self, key_size=KEY_SIZE):
        self.key_size = key_size

    def ap_start(self):
        """Generate initial data for AP. Will be passed to assoc_client later as ap_data"""
        #This is the master key to deassoc all clients if the ap goes down
        p2 = sympy.randprime(2**(self.key_size-1),(2**self.key_size)-1)
        q2 = sympy.randprime(2**(self.key_size-1),(2**self.key_size)-1)
        N2 = p2*q2
        return {"envelope": N2, "letter": p2}

    def ap_assoc(self, ap_data, body):
        if not "envelope" in body:
            return (False)
        pi = sympy.randprime(2**(self.key_size-1),(2**self.key_size)-1)
        qi = sympy.randprime(2**(self.key_size-1),(2**self.key_size)-1)
        Ni = pi*qi
        return (True, {"client_envelope": body["envelope"], "ap_letter": pi}, {"envelopes": [Ni, ap_data["envelope"]]})
    
    def ap_verify_deauth(self, ap_data, client_data, body):
        if not "letter" in body:
            return False
        p = client_data["client_envelope"] / body["letter"]
        if p%1.0 != 0:
            return False
        return True
    
    def ap_deauth_client(self, ap_data, client_data):
        return {"letter": client_data["ap_letter"]}
    
    def ap_deauth_all(self, ap_data):
        return {"letter": ap_data["letter"]}
    
    def client_assoc(self):
        p1 = sympy.randprime(2**(self.key_size-1),(2**self.key_size)-1)
        q1 = sympy.randprime(2**(self.key_size-1),(2**self.key_size)-1)
        N1 = p1*q1
        return ({"letter": p1}, {"envelope": N1})
    
    def client_verify_deauth(self, ap_data, body):
        if not "letter" in body:
            return False
        for envelope in ap_data["envelopes"]:
            p = envelope/body["letter"]
            if p%1 == 0:
                return True
        return False
