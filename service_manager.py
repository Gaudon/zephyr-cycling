class ServiceLocator:
    def __init__(self):
        self.services = []


    def register(self, service):
        self.services.append(service)
        print("[ServiceLocator] : Service Registered [{}]".format(type(service).__name__))
        
        
    def get(self, service_class):
        for service in self.services:
            if isinstance(service, service_class):
                return service
        raise Exception("[SYSTEM] : Service Failure - Required Service Missing")
    
    
    def get_services(self):
        return self.services
    
    
    def list_services(self):
        for service in self.services:
            print(type(service).__name__)

# Global Service Locator Instance
service_locator = ServiceLocator()