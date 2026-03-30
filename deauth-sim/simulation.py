#import multiprocessing as mp
import threading
import time

class Ether:
    def __init__(self):
        #manager = mp.Manager()
        self.shared = {}
        self.write = threading.Lock()
        self.read = threading.Event()
        self.read_end = threading.Condition()
        self.shared["readers"] = 0
    
    def send(self, message):
        with self.write:
            #time.sleep(1)
            self.shared["message"] = message
            self.read.set()
            # with self.read_end:
                # self.read_end.wait_for(lambda: self.shared["readers"] == 0)
            self.read.clear()
    
    def recv(self, timeout=None):
        #with self.write:
        #    self.shared["readers"] += 1
        result = None
        if self.read.wait(timeout):
            result = self.shared["message"]
        self.shared["readers"] -= 1
        #with self.read_end:
        #    self.read_end.notify()
        return result

SUBTYPE_ASSOC_REQ = 0b0000
SUBTYPE_ASSOC_RESP = 0b0001
SUBTYPE_PROBE_REQ = 0b0100
SUBTYPE_PROBE_RESP = 0b0101
SUBTYPE_AUTH = 0b1011
SUBTYPE_DEAUTH = 0b1100

ADDRESS_BROADCAST = "ff:ff:ff:ff:ff:ff"

class Frame:
    def __init__(self, type, subtype, src, dest, body):
        self.type = type
        self.subtype = subtype
        self.src = src
        self.dest = dest
        self.body = body
    
    def __repr__(self):
        return "Frame(type=%d, subtype=%d, src=%s, dest=%s, body=%s)" % (self.type, self.subtype, self.src, self.dest, self.body.__repr__())
    
    @staticmethod
    def probe_req(src, body):
        return Frame(0, SUBTYPE_PROBE_REQ, src, ADDRESS_BROADCAST, body)
    
    @staticmethod
    def probe_resp(src, dest, body):
        return Frame(0, SUBTYPE_PROBE_RESP, src, dest, body)
    
    @staticmethod
    def auth(src, dest, body):
        return Frame(0, SUBTYPE_AUTH, src, dest, body)

    @staticmethod
    def assoc_req(src, dest, body):
        return Frame(0, SUBTYPE_ASSOC_REQ, src, dest, body)

    @staticmethod
    def assoc_resp(src, dest, body):
        return Frame(0, SUBTYPE_ASSOC_RESP, src, dest, body)
    
    @staticmethod
    def deauth(src, dest, body):
        return Frame(0, SUBTYPE_DEAUTH, src, dest, body)

def recv_packet(ether: Ether, dest, type, subtype, timeout=None):
    start = time.time()
    end = None
    if timeout != None:
        end = start + timeout
    while timeout==None or time.time() < end:
        next: Frame = ether.recv(end-time.time() if timeout != None else None)
        if next.dest == dest and next.type == type and next.subtype == subtype:
            return next

class AccessPoint:
    def __init__(self, ether: Ether, mac, protocol, ssid):
        self.mac = mac
        self.protocol = protocol
        self.ether = ether
        self.ssid = ssid
        self.clients = {}
        self.protocol_data = protocol.ap_start()
        #self.p = mp.Process(target=self.listen)
        self.p = threading.Thread(target=self.listen)
        self.p.start()

    def listen(self):
        while(True):
            frame: Frame = self.ether.recv()
            if frame.dest == self.mac or frame.dest == ADDRESS_BROADCAST:
                #Addressed to this AP
                print("AP", self.mac, "recv", frame)
                if frame.type == 0:
                    #Managment frame
                    if frame.subtype == SUBTYPE_PROBE_REQ:
                        print("AP", self.mac, "Got probe, responding")
                        resp = Frame.probe_resp(self.mac, frame.src, {"ssid": self.ssid})
                        self.ether.send(resp)
                    elif frame.subtype == SUBTYPE_AUTH:
                        if frame.body["seq"] == 1:
                            if frame.src in self.clients:
                                self.ether.send(Frame.auth(self.mac, frame.src, {"status": 1}))
                            else:
                                self.clients[frame.src] = {"auth": True}
                                self.ether.send(Frame.auth(self.mac, frame.src, {"seq": 2, "status": 0}))
                        else:
                            self.ether.send(Frame.auth(self.mac, frame.src, {"status": 1}))
                    elif frame.subtype == SUBTYPE_ASSOC_REQ:
                        #This is where spicy protocol stuff goes
                        #Drop frame if client not auth'd
                        if frame.src in self.clients:
                            success, client_data, response_body = self.protocol.ap_assoc(self.protocol_data, frame.body)
                            if success:
                                self.clients[frame.src]["assoc"] = True
                                self.clients[frame.src]["assoc_data"] = client_data
                                self.ether.send(Frame.assoc_resp(self.mac, frame.src, response_body))
                    elif frame.subtype == SUBTYPE_DEAUTH:
                        if frame.src in self.clients:
                            if self.protocol.ap_verify_deauth(self.protocol_data, self.clients[frame.src]["assoc_data"], frame.body):
                                self.clients.pop(frame.src)
                                print("AP", self.mac, "Deauth by request", frame.src)
    
    def deauth_client(self, client_mac):
        if not client_mac in self.clients:
            print(self.clients)
        client = self.clients[client_mac]
        self.ether.send(Frame.deauth(self.mac, client_mac, self.protocol.ap_deauth_client(self.protocol_data, client["assoc_data"])))
    
    def deauth_all(self):
        self.ether.send(Frame.deauth(self.mac, ADDRESS_BROADCAST, self.protocol.ap_deauth_all(self.protocol_data)))
    
    def client_connected(self, client_mac):
        return client_mac in self.clients

    def join(self):
        self.p.join()

class Client:
    def __init__(self, ether: Ether, mac, protocol):
        self.ether = ether
        self.protocol = protocol
        self.mac = mac
        self.connected = False
        #self.p = mp.Process(target=self.listen)
        self.p = threading.Thread(target=self.listen)

    def connect(self):
        self.ether.send(Frame.probe_req(self.mac, {}))
        probe_resp = recv_packet(self.ether, self.mac, 0, SUBTYPE_PROBE_RESP, 10)
        if probe_resp == None:
            print("Client", self.mac, "No probe response")
            return False
        ap_mac = probe_resp.src
        ap_ssid = probe_resp.body["ssid"]
        print("Client", self.mac, "Connecting to", ap_ssid)
        self.ether.send(Frame.auth(self.mac, ap_mac, {"seq": 1}))
        auth_resp = recv_packet(self.ether, self.mac, 0, SUBTYPE_AUTH, 10)
        if auth_resp == None:
            print("Client", self.mac, "No auth response")
            return False
        if auth_resp.body["status"] != 0:
            print("Client", self.mac, "connect to", ap_ssid, "failed auth. Status:", auth_resp.body["status"])
            return False
        
        #Protocol specific data gen
        self.deauth_body, assoc_body = self.protocol.client_assoc()
        self.ether.send(Frame.assoc_req(self.mac, ap_mac, assoc_body))
        assoc_resp = recv_packet(self.ether, self.mac, 0, SUBTYPE_ASSOC_RESP, 10)
        if assoc_resp == None:
            print("Client", self.mac, "No assoc response")
            return False
        self.ap_assoc = assoc_resp.body
        print("Client", self.mac, "Associated with ap", ap_ssid)
        self.ap_mac = ap_mac
        self.ap_ssid = ap_ssid
        self.connected = True
        self.p.start()
        return True
    
    def listen(self):
        while self.connected:
            frame: Frame = self.ether.recv()
            if frame.dest == self.mac or frame.dest == ADDRESS_BROADCAST:
                #Addressed to this AP
                print("Client", self.mac, "recv", frame)
                if frame.type == 0:
                    #Management
                    if frame.subtype == SUBTYPE_DEAUTH:
                        if self.protocol.client_verify_deauth(self.ap_assoc, frame.body):
                            self._disconnected()
                            print("Client", self.mac, "Deauth by request from", self.ap_ssid)
    
    def deauth(self):
        self.ether.send(Frame.deauth(self.mac, self.ap_mac, self.deauth_body))
        self._disconnected()
        print("Client", self.mac, "Deauth from", self.ap_ssid)
    
    def _disconnected(self):
        self.connected = False
        #self.p = mp.Process(target=self.listen)
        self.p = threading.Thread(target=self.listen)