from __future__ import annotations

import subprocess
import os
import time

from sysmind.logging import logger


class Sysctl(object):
  def __init__(self, sync=True, log_errors=True, backup_config=True):
    if os.path.exists('/sbin/sysctl'):
      self._sysctl = '/sbin/sysctl'
    else:
      self._sysctl = 'sysctl'
      
    self._log_errors = log_errors
    self._sync = sync
    self._backup_config = backup_config
    
    sysctl_status = False
    try:
      output = subprocess.check_output([self._sysctl, '-a'], text=True)
      sysctl_status = True
    except Exception as e:
      if log_errors is True:
        logger.error(f'Failed to get sysctl values. Error: {e}')
    
    if sysctl_status is True and output is not None:
      for line in output.splitlines():
        data = line.split('=')
        name = data[0].strip()
        value = data[1].strip()
        self.__dict__[name] = value
        
      
  def __repr__(self):
    return self._sysctl
  
  def __str__(self):
    # Dispaly 'sysctl -a' variables
    string = []
    for name, value in self.__dict__.items():
      string.append(f'{name} = {value}')
    
    return '\n'.join(string)
  
  def __getitem__(self, name):
    return self.__dict__[name]
  
  def __setitem__(self, name, value):
    self.__dict__[name] = value
    
    if self._sync is True:
      if os.path.isfile('/etc/sysctl.conf') and self._backup_config is True:
        # Copy file /etc/sysctl.conf.<timestamp>
        try:
          os.system(f'cp /etc/sysctl.conf /etc/sysctl.conf.{int(time.time())}.bkp')
        except Exception as e:
          if self._log_errors is True:
            logger.error(f'Failed to copy file /etc/sysctl.conf. Error: {e}')
      
      # Write sysctl.conf
      try:
        with open('/etc/sysctl.conf', 'w') as f:
          sysctl_conf = []
          
          for name, value in self.__dict__.items():
            sysctl_conf.append(f'{name} = {value}')
          
          f.write('\n'.join(sysctl_conf))
          
          result = subprocess.run([self._sysctl, '-w', f'{name}={value}'], capture_output=True)
          if result.returncode != 0:
            if self._log_errors is True:
              logger.error(f"Error setting sysctl value: {result.stderr}")
      except Exception as e:
        if self._log_errors is True:
          logger.error(f'Failed to write sysctl.conf. Error: {e}')
          
    
  
    
  def __getattr__(self, name):
    if name in self.__dict__:
      return self.__dict__[name]
    else:
      raise AttributeError(name)
    
  def __setattr__(self, name, value):
    if name in self.__dict__:
      self.__dict__[name] = value
    
    
      if self._sync is True:
        if os.path.isfile('/etc/sysctl.conf') and self._backup_config is True:
          # Copy file /etc/sysctl.conf.<timestamp>
          try:
            os.system(f'cp /etc/sysctl.conf /etc/sysctl.conf.{int(time.time())}.bkp')
          except Exception as e:
            if self._log_errors is True:
              logger.error(f'Failed to copy file /etc/sysctl.conf. Error: {e}')

        # Write sysctl.conf
        try:
          with open('/etc/sysctl.conf', 'w') as f:
            sysctl_conf = []
            
            for name, value in self.__dict__.items():
              sysctl_conf.append(f'{name} = {value}')
            
            f.write('\n'.join(sysctl_conf))
            
            result = subprocess.run([self._sysctl, '-w', f'{name}={value}'], capture_output=True)
            if result.returncode != 0 and self._log_errors is True:
              logger.error(f"Error setting sysctl value: {result.stderr}")
        except Exception as e:
          if self._log_errors is True:
            logger.error(f'Failed to write sysctl.conf. Error: {e}')
    else:
      if self._log_errors is True:
        logger.error(f"Sysctl object has no attribute: {name}")
      raise AttributeError(name)
    
  def sync(self):
    if self._sync is True:
      logger.error(f'Sync function is does not need to be called directly when using in Sysctl(sync=True)')
      
    else:
      if os.path.isfile('/etc/sysctl.conf') and self._backup_config is True:
        # Copy file /etc/sysctl.conf.<timestamp>
        try:
          os.system(f'cp /etc/sysctl.conf /etc/sysctl.conf.{int(time.time())}.bkp')
        except Exception as e:
          if self._log_errors is True:
            logger.error(f'Failed to copy file /etc/sysctl.conf. Error: {e}')
      
      # Write sysctl.conf
      try:
        with open('/etc/sysctl.conf', 'w') as f:
          sysctl_conf = []
          
          for name, value in self.__dict__.items():
            sysctl_conf.append(f'{name} = {value}')
          
          f.write('\n'.join(sysctl_conf))
      except Exception as e:
        if self._log_errors is True:
          logger.error(f'Failed to write sysctl.conf. Error: {e}')
          
    
  
  