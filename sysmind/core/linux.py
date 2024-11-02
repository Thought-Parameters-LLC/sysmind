# systemind/core/linux.py
from __future__ import annotations

import subprocess

from sysmind.logging import logger
from sysmind.core.os import OperatingSystem

import distro

def get_distro_id():
  try:
    return distro.id().lower()
  except Exception as e:
    logger.error(e)
    return None
    
def get_distro_name():
  try:
    return distro.name().lower()
  except Exception as e:
    logger.error(e)
    return None
  
def get_distro_like():
  try:
    return distro.like().lower()
  except Exception as e:
    logger.error(e)
    return None

    
class Linux(OperatingSystem):
  
  def __init__(self):
    super().__init__()
    
    # Get Linux distribution id
    self._id = get_distro_id()
    self._name = get_distro_name()
    self._like = get_distro_like()
    if self._like is not None:
      if 'debian' in self._like:
        self._pkg_manager = 'apt'
      elif 'rhel' in self._like:
        self._pkg_manager = 'yum'
      else:
        logger.warning('Linux distribution not supported')
        self._pkg_manager = None  
    else:
      logger.warning('Linux distribution not supported')
      self._pkg_manager = None
    
    logger.info(f'Detected Linux distribution: {self._name} ({self._id})')
    
    @property
    def id(self):
      return self._id
    
    @property
    def name(self):
      return self._name
    
    @property
    def like(self):
      return self._like
    
    @property
    def pkg_manager(self):
      return self._pkg_manager
    
    

__all__ = ['Linux']