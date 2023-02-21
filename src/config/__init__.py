
import json
import os

def getConfig(env_server=""):
    if not env_server:
        env_server = os.environ.get("env_server", "")
    print("env_server=%s" % (os.environ.get("env_server", "")))
    # print("test2=%s" % (os.environ.get("test2", "")))

    basedir = os.path.abspath(os.path.dirname(__file__))
    jsonfile = "%s/dev.json" % (basedir)

    if(env_server == "vpc_localhost"):
        jsonfile = "%s/dev.json" % (basedir)
    elif(env_server == "vpc_zeyou" ):
        jsonfile = "%s/prod.json" % (basedir)
    else:
        jsonfile = "%s/dev.json" % (basedir)

    config = json.loads("{}")
    try:
        with open(jsonfile, encoding='utf-8') as f:
            config = json.loads(f.read())
            print("============current config :============")
            print(config)
    except Exception as ex:
        print(ex)

    return config

if __name__ == "__main__":
    def test(p=""):
        if not p:
            p= "in if"
            print(p)

    test()