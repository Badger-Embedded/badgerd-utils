"""Power Control for Lab

Usage:
  psu_control status [<codename> <device_id> <key>] [options]
  psu_control switch <codename> (on|off|toggle) [options]
  psu_control (-h | --help)
  psu_control --version

Options:
  --config=PATH   Path of config file which contains essential informations [default: ~/.psu_control.config]
  -h --help       Show this screen.
  --version       Show version.
"""
from docopt import docopt
import tinytuya
import os
import json
import sys


#https://github.com/jasonacox/tinytuya

def get_device_status(tuya_device, codename, configs):
  dps_status = False
  if codename and codename in configs["codenames"]:
    dps_status = tuya_device.status()['dps'][configs["codenames"][codename]]
  return dps_status

def main():
  arguments = docopt(__doc__, version='psu_control 0.1')
  config_path = arguments['--config']
  codename = arguments['<codename>']

  if config_path == '~/.psu_control.config':
    config_path = os.path.join(os.environ['HOME'], '.psu_control.config')

  print(f"Config path: {config_path} Home: {os.environ['HOME']}")

  # check if the config exists, if not then we will create an empty one
  if not os.path.isfile(config_path):
    with open(config_path, 'w'):
      pass


  # read config file and get the necessary values
  with open(config_path, 'r') as config_file:
    configs = json.load(config_file)

    device_id = arguments["<device_id>"] or configs['dev_id']
    local_key = arguments["<key>"] or configs['local_key']
    address = configs['address']
    version = configs['version']

  d = tinytuya.OutletDevice(
    dev_id=device_id,
    address=address,
    local_key=local_key,
    version=version
  )


  if arguments['status']:
    status = d.status()
    if codename and codename in configs["codenames"]:
      dps_status = get_device_status(d, codename, configs)
      print(f'Status of {codename}: {dps_status}')
    else:
      print(f'Status {status}')
  elif arguments['switch']:
    if not codename in configs["codenames"]:
      print("Invalid codename!")
      sys.exit(-1)
    if arguments['on'] or arguments['off']:
      d.set_status(arguments['on'], configs["codenames"][codename])
      print(f"Status of {codename} set to {arguments['on']}")
    elif arguments['toggle']:
      dps_status = not get_device_status(d, codename, configs)
      d.set_status(dps_status, configs["codenames"][codename])
      print(f"Status of {codename} set to {dps_status}")

if __name__ == '__main__':
  main()
