import multiprocessing as mp

class Ether:
    def __init__(self):
        manager = mp.Manager()
        self.val = manager.dict()
        self.write = manager.Lock()
        self.read = manager.Event()
    
    def send(self, message):
        with self.write:
            self.val["message"] = message
            self.read.set()
        self.read.clear()
    
    def recv(self):
        self.read.wait()
        return self.val["message"]

class AccessPoint:
    def __init__(self, mac, protocol, ether):
        self.mac = mac
        self.protocol = protocol
        self.ether = ether
        self.p = mp.Process(target=self.listen)
        self.p.start()

    def listen(self):
        print(self.ether.recv())
    
    def join(self):
        self.p.join()