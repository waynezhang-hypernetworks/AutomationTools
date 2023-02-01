import sys
from io import StringIO
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import CommitError, ConfigLoadError

class DevNull:
    def write(self, msg):
        pass
sys.stderr = DevNull()

def redirect_output(my_result):
    tmp = sys.stdout
    my_result = StringIO()
    sys.stdout = my_result
    sys.stdout = tmp
    results = my_result.getvalue()
    data_results = results.strip()
    return data_results

AS = input("please insert access switch number:")
dev = Device(host=f'10.1.252.{AS}', user='hyperadmin', password='dAJr3Ear$z#G*Y').open()
cu = Config(dev)

version = dev.cli("show version").split('\n')[4]
if version == "Model: ex2300-c-12t":
    MODE = "interface-mode"
else:
    MODE = "port-mode"

print(f"\nshowing AS{AS} interfaces and COS configuration...")
show_int = dev.cli("show configuration interfaces")
show_cos = dev.cli("show configuration class-of-service")
print(show_int)
print(show_cos)

print("\ncleaning up interfaces and cos...")
try:
    cu.load(f"wildcard range set interfaces ge-0/0/[0-11] unit 0 family ethernet-switching {MODE} access", format="set", merge=True)
except ConfigLoadError:
    pass
try:
    cu.load("wildcard range delete interfaces ge-0/0/[0-11]", format="set", merge=True)
except ConfigLoadError:
    pass
try:
    cu.load(f"wildcard range set interfaces ge-0/0/[0-11] unit 0 family ethernet-switching {MODE} access", format="set", merge=True)
except ConfigLoadError:
    pass
try:
    cu.load("set class-of-service interfaces ge-0/0/0 shaping-rate 12m", format="set")
except ConfigLoadError:
    pass
try:
    cu.load("delete class-of-service interfaces", format="set")
except ConfigLoadError:
    pass

print("-" * 15 + "show compare" + "-" * 15)

def redirect_output():
    tmp = sys.stdout
    my_result = StringIO()
    sys.stdout = my_result
    show_compare = cu.pdiff()
    sys.stdout = tmp
    results = my_result.getvalue()
    return results

print(redirect_output())
print(type(redirect_output()))

COMMIT = input("would you like to commit the configuration? (yes or no): ")
if COMMIT.upper() == "YES":
    try:
        cu.commit()
        print(f"AS{AS} clean up has been configured and commited.")
    except CommitError as e:
        print(e)
else:
    cu.rollback()
    print("Configuration cancelled and has been rolledback")

dev.close()