from pymysql_manager import ConnectionManager
from src.config import getConfig

config = getConfig()
m = ConnectionManager(default='diancan',
                    diancan=dict(host=config["mysql"]["diancan"]["host"],
                                 port=config["mysql"]["diancan"]["port"],
                                 user=config["mysql"]["diancan"]["user"],
                                 password=config["mysql"]["diancan"]["password"],
                                 database=config["mysql"]["diancan"]["database"],
                                 charset='utf8'),
                    )