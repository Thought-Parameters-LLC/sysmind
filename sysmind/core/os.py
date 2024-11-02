from __future__ import annotations

from socket import close, gethostname as _gethostname
from python_hosts import Hosts as _Hosts
from dns.resolver import Resolver as _Resolver

import psutil
import netifaces
import subprocess
import os

from platform import system as _system
from platform import version as _version
from platform import architecture as _architecture

from sysmind.logging import logger

def get_ip(interface_name):
  
  interfaces = netifaces.interfaces()
  
  if interface_name in interfaces:
    addrs = netifaces.ifaddresses(interface_name)
    return addrs[netifaces.AF_INET][0]['addr']
  else:
    logger.error(f'Interface {interface_name} does not exist.')
  
  return None

def get_mac(interface_name):
  
  interfaces = netifaces.interfaces()
  
  if interface_name in interfaces:
    addrs = netifaces.ifaddresses(interface_name)
    return addrs[netifaces.AF_LINK][0]['addr']
  else:
    logger.error(f'Interface {interface_name} does not exist.')
  
def get_ports():
  
  # Get a list of all connections
  connections = psutil.net_connections(kind='inet')
  
  listening_ports = []
  established_connections = []
  closed_connections = []
  
  for conn in connections:
    laddr = conn.laddr
    raddr = conn.raddr
    
    if conn.status == psutil.CONN_LISTEN:
      listening_ports.append({
        'local_ip': laddr.ip,
        'local_port': laddr.port,
        'status': conn.status
      })
      
    elif conn.status == psutil.CONN_ESTABLISHED:
      established_connections.append({
        'local_ip': laddr.ip,
        'local_port': laddr.port,
        'remote_ip': raddr.ip,
        'remote_port': raddr.port,
        'status': conn.status
      })
      
    elif conn.status == psutil.CONN_CLOSE_WAIT:
      closed_connections.append({
        'local_ip': laddr.ip,
        'local_port': laddr.port,
        'remote_ip': raddr.ip,
        'remote_port': raddr.port,
        'status': conn.status
      })
      continue
      
    elif conn.status == psutil.CONN_CLOSE:
      closed_connections.append({
        'local_ip': laddr.ip,
        'local_port': laddr.port,
        'remote_ip': raddr.ip,
        'remote_port': raddr.port,
        'status': conn.status
      })
      
    elif conn.status == psutil.CONN_NONE:
      closed_connections.append({
        'local_ip': laddr.ip,
        'local_port': laddr.port,
        'remote_ip': raddr.ip,
        'remote_port': raddr.port,
        'status': conn.status
      })
      
    else:
      logger.info(f'Connection from {laddr.ip}:{laddr.port} to {raddr.ip}:{raddr.port} {conn.status}.')
      continue
      
  return {'listening_ports': listening_ports, 'established_connections': established_connections, 'closed_connections': closed_connections}
  
def get_services():
  os_name = _system().lower()
  
  if os_name == 'darwin':
    return get_services_macos()
  elif os_name == 'windows':
    return get_services_windows()
  elif os_name == 'linux':
    return get_services_linux()
  else:
    return None
  
def get_services_macos():
  # Use launchctl to get macOS services
  try:
    output = subprocess.check_output(['launchctl', 'list'], text=True)
    services = []
    for line in output.splitlines()[1:]:
      parts = line.split()[1:]
      if len(parts) > 1:
        services.append({
          'name': parts[-1],
          'status': parts[0],
        })
        
    return services
  except Exception as e:
    logger.error(f'Failed to get macOS services. Error: {e}')
    return []
  
def get_services_windows():
  services = []
  for service in psutil.win_service_iter():
    services.append({
      'name': service.name(),
      'status': service.status(),
      'description': service.display_name()
    })
    
  return services

def get_services_linux():
  # Try to list services using systemd for Linux
  try:
      output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=running'], text=True)
      services = []
      for line in output.splitlines()[1:]:
          parts = line.split()
          if len(parts) > 1:
              services.append({
                  "name": parts[0],
                  "status": parts[3],
              })
      return services
  except Exception as e:
      print(f"Error retrieving services on Linux: {e}")
      return []
    
def get_processes():
  return [{'pid': p.pid, 'name': p.name(), 'cmdline': ' '.join(p.cmdline())} for p in psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'status']) if p.status() != psutil.STATUS_STOPPED]

def get_usb_devices():
  import libusb_package
  import usb.core
  import usb.util
  import usb.backend.libusb1 as libusb1
  
  libusb1_backend = libusb1.get_backend(find_library=libusb1.find_library)
  
  usb_devices = []
  
  devices = usb.core.find(find_all=True, backend=libusb1_backend)
  
  for device in devices:
    usb_devices.append({
      'idVendor': hex(device.idVendor),
      'idProduct': hex(device.idProduct),
      'manufacturer': usb.util.get_string(device, device.iManufacturer),
      'serial_number': device.serial_number,
      'bus': device.bus,
      'address': device.address,
      'product': device.product
    })
    
  return usb_devices

def normalize_device_info(
  vendor_id=None,
  device_id=None,
  vendor_name=None,
  device_name=None
):
  return {
    'vendor_id': vendor_id,
    'device_id': device_id,
    'vendor_name': vendor_name,
    'device_name': device_name,
  }
  
def get_pci_devices_linux():
  devices = []
  try:
    output = subprocess.check_output(['lspci', '-vnn'], text=True)
    device_info = {}
    for line in output.splitlines():
      if line.strip() == '':
        if device_info:
          devices.append(device_info)
          device_info = {}
          
      else:
        key, value = line.split('\t', 1)
        if key == "Vendor":
          device_info['vendor_id'] = value
        if key == "Device":
          device_info['device_name'] = value
        if key == "Slot":
          device_info['vendor_id'], device_info['device_id'] = value.split(':')[0], value.split(':')[1]
          
      if device_info:
        devices.append(device_info)
  except Exception as e:
    logger.error(f'Failed to get PCI devices. Error: {e}')
    
    return [normalize_device_info(**d) for d in devices]
  
def get_pci_devices_windows():
  devices = []
  try:
    import wmi
    c = wmi.WMI()
    for device in c.Win32_PnPEntity():
      if 'PCI' in device.PNPDeviceID:
        devices.append(normalize_device_info(
          vendor_id=device.PNPDeviceID.split("\\")[1].split("&")[0].replace('VEN_', ''),
          device_id=device.PNPDeviceID.split("&")[1].replace('DEV_', ''),
          vendor_name=device.Manufacturer,
          device_name=device.Description
        ))
        
  except Exception as e:
    logger.error(f'Failed to get PCI devices. Error: {e}')
    
  return devices

def get_pci_devices_macos():
  devices = []
  try:
    output = subprocess.check_output(['system_profiler', 'SPPCIDataType'], text=True)
    current_device = {}
    for line in output.splitlines():
        if "Vendor" in line:
            current_device['vendor_name'] = line.split(":")[-1].strip()
        if "Device" in line:
            current_device['device_name'] = line.split(":")[-1].strip()
        if "Vendor ID" in line:
            current_device['vendor_id'] = line.split(":")[-1].strip()
        if "Device ID" in line:
            current_device['device_id'] = line.split(":")[-1].strip()
        if line.strip() == "":
            if current_device:
                devices.append(current_device)
                current_device = {}
    if current_device:
        devices.append(current_device)

  except Exception as e:
    logger.error(f'Failed to get PCI devices. Error: {e}')
    
  return [normalize_device_info(**d) for d in devices]

def get_pci_devices():
  os_name = _system.lower()
  
  if os_name == 'darwin':
    return get_pci_devices_macos()
  elif os_name == 'windows':
    return get_pci_devices_windows()
  elif os_name == 'linux':
    return get_pci_devices_linux()
  else:
    return None
  
def get_hosts():
 
  try:
    hosts = _Hosts().entries
    hosts_file = _Hosts().determine_hosts_path()
  except Exception as e:
    logger.error(f'Failed to retrieve hosts info. Error: {e}')
    return None
  
  if not hosts or len(hosts) == 0:
    logger.warning(f'Failed to get any hosts info from file "{hosts_file}".')
    return None
  
  return hosts

def get_resolver():
  try:
    resolver = {
      'nameservers': _Resolver().nameservers,
      'search': _Resolver().search,
      'port': _Resolver().port,
      'domain': _Resolver().domain,
      'retry_servfail': _Resolver().retry_servfail,
      'timeout': _Resolver().timeout,
      'lifetime': _Resolver().lifetime,
      'edns': _Resolver().edns,
      'ednsflags': _Resolver().ednsflags,
    }
  except Exception as e:
    logger.error(f'Failed to retrieve resolver info. Error: {e}')
    return None

  return resolver

def get_posix_compliant():
  os_name = _system().lower()
  
  if os_name in ['linux', 'darwin']:
    try:
      #Try using POSIX function
      uname_info = os.uname()
      return True
    except AttributeError:
      logger.info('POSIX function not available on this system.')
      return False
  elif os_name == 'windows':
    # Windows is not POSIX-compliant, but we can detect if it's running in a
    # POSIX-likeenvironment by checking '/proc/version'
    try:
      # WSL has a Linux kernel, check for presence of '/proc/version'
      with open('/proc/version', 'r') as f:
        if 'microsoft' in f.read().lower():
          return True
    except FileNotFoundError:
      # Normal Windows environment, not POSIX-compliant
      return False
  else:
    logger.warning(f'Unsupported operating system: {os_name}')
    return False
  
  
def get_kernel_name():
  os_name = _system().lower()
  
  if os_name in ['linux', 'darwin']:
    return os.uname().sysname
  elif os_name == 'windows':
    return 'Windows'
  else:
    logger.warning(f'Unsupported operating system: {os_name}')
    return None
  
def get_kernel_version():
  os_name = _system().lower()

  if os_name in ['linux', 'darwin']:
    return os.uname().release
  elif os_name == 'windows':
    return _version()
  else:
    logger.warning(f'Unsupported operating system: {os_name}')
    return None
  
class OperatingSystem:
  def __init__(self):
    self._name = _system().lower()
    self._version = _version()
    self._arch = _architecture()
    self._hostname = _gethostname()
    
    # Get number of cpus
    self._cpu_count = psutil.cpu_count()
    
    # Get cpu frequency
    self._cpu_frequency = psutil.cpu_freq().max
    
    # Get system memory
    self._memory = psutil.virtual_memory().total
    
    # Get swap memory
    self._swap = psutil.swap_memory().total
    
    # Get mounts info
    self._mounts = psutil.disk_partitions(all=True)
    
    # Get usb device info
    self._usb_devices = get_usb_devices()
    
    # Get pci/pcie device info
    self._pci_devices = get_pci_devices()
    
    # Get hosts info
    self._hosts = get_hosts()
    
    # Get resolver info
    self._resolver = get_resolver()
    
    # Get if the OS is posix-compliant
    self._posix_compliant = get_posix_compliant()
    
    # Get kernel name
    self._kernel_name = get_kernel_name()
    
    # Get kernel_version
    self._kernel_version = get_kernel_version()
    
    if self._name == 'darwin':
      self._name = 'macos'
      self._ip = get_ip('en0')
      self._mac = get_mac('en0')

    elif self._name == 'windows':
      self._name = 'windows'
      self._ip = get_ip('Ethernet')
      self._mac = get_mac('Ethernet')
      
    elif self._name == 'linux':
      self._name = 'linux'
      self._ip = get_ip('eth0')
      self._mac = get_mac('eth0')

    else:
      self._ip = None
      self._mac = None
      
    self._interfaces = [{'name': interface, 'ip': get_ip(interface), 'mac': get_mac(interface)} for interface in netifaces.interfaces()]
    
    self._ports = get_ports()
    self._services = get_services()
    self._processes = get_processes()
      
  def __str__(self):
    return self.name

  @property
  def name(self):
    return self._name

  @property
  def version(self):
    return self._version

  @property
  def arch(self):
    return self._arch
  
  @property
  def hostname(self):
    return self._hostname
  
  @property
  def cpu_count(self):
    return self._cpu_count
  
  @property
  def cpu_frequency(self):
    return self._cpu_frequency
  
  @property
  def memory(self):
    return self._memory
  
  @property
  def swap(self):
    return self._swap
  
  @property
  def mounts(self):
    return self._mounts
  
  @property
  def usb_devices(self):
    return self._usb_devices
  
  @property
  def pci_devices(self):
    return self._pci_devices
  
  @property
  def hosts(self):
    return self._hosts
  
  @property
  def resolver(self):
    return self._resolver
  
  @property
  def posix_compliant(self):
    return self._posix_compliant
  
  @property
  def kernel_name(self):
    return self._kernel_name
  
  @property
  def kernel_version(self):
    return self._kernel_version
  
  @property
  def ip(self):
    return self._ip
  
  @property
  def mac(self):
    return self._mac
  
  @property
  def interfaces(self):
    return self._interfaces
  
  @property
  def ports(self):
    return self._ports
  
  @property
  def services(self):
    return self._services
  
  @property
  def processes(self):
    return self._processes