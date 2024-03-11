from utils.constants import *
from utils.util import *

class CameraConnectorConfig:
    
    def __init__(self):
        self.cameraEndpoint = 0
        self.remoteExecutorEndpoint = None
        self.localExecutorEndpoint = 'http://127.0.0.1:5001'
        self.appId = "65bd5b4573f487d9b6cdebfe"
        self.secretKey = "Wesley Clover"
    
    def setConfig(self, config):
        '''
            Registering config in local system
        '''
        if not config:
            print("No config ... ")
            return
        try:
            self.cameraEndpoint = convertSringToInteger(removeSpaces(config.get(Constants.CAM_ENDPOINT, "0")))
            self.remoteExecutorEndpoint = removeSpaces(config.get(Constants.REMOTE_ENDPOINT, "http://127.0.0.1:5001"))
            self.localExecutorEndpoint = removeSpaces(config.get(Constants.LOCAL_ENDPOINT, "http://127.0.0.1:5001"))
        except Exception as e:
            print(f"Exception: {e}")
            self.cameraEndpoint = 0
            self.remoteExecutorEndpoint = None
            self.localExecutorEndpoint = None