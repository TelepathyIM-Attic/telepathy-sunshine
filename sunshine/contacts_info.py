# telepathy-sunshine is the GaduGadu connection manager for Telepathy
#
# Copyright (C) 2010 Krzysztof Klinikowski <kkszysiu@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import logging
import dbus
import dbus.service

from sunshine.Connection_Interface_Contact_Info import ConnectionInterfaceContactInfo

import telepathy
import telepathy.constants
import telepathy.errors

from sunshine.handle import SunshineHandleFactory
from sunshine.util.decorator import async

__all__ = ['SunshineContactInfo']

logger = logging.getLogger('Sunshine.ContactInfo')

CONNECTION_INTERFACE_CONTACT_INFO = 'org.freedesktop.Telepathy.Connection.Interface.ContactInfo.DRAFT'

# Contact_Info_Flag
CONTACT_INFO_FLAG_CAN_SET = 1
CONTACT_INFO_FLAG_PUSH = 2
LAST_CONTACT_INFO_FLAG = 2
# Contact_Info_Field_Flags (bitfield/set of flags, 0 for none)
CONTACT_INFO_FIELD_FLAG_PARAMETERS_MANDATORY = 1

class SunshineContactInfo(telepathy.server.DBusProperties, ConnectionInterfaceContactInfo):
    def __init__(self):
        logger.info('SunshineContactInfo called.')
        telepathy.server.DBusProperties.__init__(self)
        ConnectionInterfaceContactInfo.__init__(self)
        #self._interfaces.remove(CONNECTION_INTERFACE_CONTACT_INFO)
        
        self._implement_property_get(CONNECTION_INTERFACE_CONTACT_INFO, {
            'ContactInfoFlags': lambda: self.contact_info_flags,
            'SupportedFields': lambda: self.contact_info_supported_fields,
        })

    @property
    def contact_info_flags(self):
        return CONTACT_INFO_FLAG_CAN_SET | CONTACT_INFO_FLAG_PUSH

    @property
    def contact_info_supported_fields(self):
        return [
                  ('nickname', [], 0, 1),
                  ('fn', [], 0, 1),
                  ('label', [], 0, 1),
                  ('bday', [], 0, 1),
                  ('url', [], 0, 1),
                  ('url', [], 0, 1),
                ]

    def GetContactInfo(self, contacts):
        logger.info("GetContactInfo")
        for contact in contacts:
            print contact
        return []

    def RefreshContactInfo(self, contacts):
        logger.info('RefreshContactInfo')
        pass
        
    def RequestContactInfo(self, contact):
        logger.info('RequestContactInfo')
        pass
        
    def SetContactInfo(self, contactinfo):
        logger.info('SetContactInfo')
        pass
