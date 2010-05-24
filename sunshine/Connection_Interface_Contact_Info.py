# -*- coding: utf-8 -*-
# Generated from the Telepathy spec
""" Copyright (C) 2008 Collabora Limited 
 Copyright (C) 2008 Nokia Corporation 

    This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
  
"""

import dbus.service


class ConnectionInterfaceContactInfo(dbus.service.Interface):
    """\
      An interface for requesting information about a contact on a given
        connection. Information is represented as a list of
        Contact_Info_Fields forming a
        structured representation of a vCard (as defined by RFC 2426), using
        field names and semantics defined therein.
    """

    def __init__(self):
        self._interfaces.add('org.freedesktop.Telepathy.Connection.Interface.ContactInfo.DRAFT')

    @dbus.service.method('org.freedesktop.Telepathy.Connection.Interface.ContactInfo.DRAFT', in_signature='au', out_signature='a{ua(sasas)}')
    def GetContactInfo(self, Contacts):
        """
        Request information on several contacts at once.  This SHOULD only
        return cached information, omitting handles for which no information is
        cached from the returned map.  For contacts without cached information,
        the information SHOULD be requested from the network, with the result
        signalled later by ContactInfoChanged.
      
        """
        raise NotImplementedError
  
    @dbus.service.method('org.freedesktop.Telepathy.Connection.Interface.ContactInfo.DRAFT', in_signature='u', out_signature='a(sasas)')
    def RequestContactInfo(self, Contact):
        """
        Retrieve information for a contact, requesting it from the network if
        it is not cached locally.
      
        """
        raise NotImplementedError
  
    @dbus.service.method('org.freedesktop.Telepathy.Connection.Interface.ContactInfo.DRAFT', in_signature='a(sasas)', out_signature='')
    def SetContactInfo(self, ContactInfo):
        """
        Set new contact information for this connection, replacing existing
        information.  This method is only suppported if
        ContactInfoFlags contains
        Can_Set, and may only be passed fields conforming to
        SupportedFields.
      
        """
        raise NotImplementedError
  
    @dbus.service.signal('org.freedesktop.Telepathy.Connection.Interface.ContactInfo.DRAFT', signature='ua(sasas)')
    def ContactInfoChanged(self, Contact, ContactInfo):
        """
        Emitted when a contact's information has changed or been received for
        the first time on this connection.
      
        """
        pass
  