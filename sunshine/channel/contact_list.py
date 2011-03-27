# telepathy-sunshine is the GaduGadu connection manager for Telepathy
#
# Copyright (C) 2006-2007 Ali Sabil <ali.sabil@gmail.com>
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
import weakref

import telepathy

import xml.etree.ElementTree as ET

from sunshine.util.decorator import async
from sunshine.handle import SunshineHandleFactory
from sunshine.channel import SunshineChannel

from sunshine.lqsoft.pygadu.twisted_protocol import GaduClient
from sunshine.lqsoft.pygadu.models import GaduProfile, GaduContact

__all__ = ['SunshineContactListChannelFactory']

logger = logging.getLogger('Sunshine.ContactListChannel')

class HandleMutex(object):
    def __init__(self):
        self._handles = set()
        self._keys = {}
        self._callbacks = {}

    def is_locked(self, handle):
        return (handle in self._handles)

    def is_owned(self, key, handle):
        return (handle in self._handles and self._keys[handle] == key)

    def lock(self, key, handle):
        if self.is_locked(handle):
            return False
        self._handles.add(handle)
        self._keys[handle] = key
        return True

    def unlock(self, key, handle):
        if not self.is_owned(key, handle):
            return
        self._handles.remove(handle)
        del self._keys[handle]
        callbacks = self._callbacks.get(handle, [])[:]
        self._callbacks[handle] = []
        for callback in callbacks:
            callback[0](*callback[1:])

    def add_callback(self, key, handle, callback):
        if self.is_owned(key, handle):
            return
        if not self.is_locked(handle):
            callback[0](*callback[1:])
        else:
            self._callbacks.setdefault(handle, []).append(callback)

class Lockable(object):
    def __init__(self, mutex, key, cb_name):
        self._mutex = mutex
        self._key = key
        self._cb_name = cb_name

    def __call__(self, func):
        def method(object, handle, *args, **kwargs):
            def finished_cb(*user_data):
                self._mutex.unlock(self._key, handle)

            def unlocked_cb():
                self._mutex.lock(self._key, handle)
                kwargs[self._cb_name] = finished_cb
                if func(object, handle, *args, **kwargs):
                    finished_cb()

            self._mutex.add_callback(self._key, handle, (unlocked_cb,))

        return method

mutex = HandleMutex()


def SunshineContactListChannelFactory(connection, manager, handle, props):
    handle = connection.handle(
        props[telepathy.CHANNEL_INTERFACE + '.TargetHandleType'],
        props[telepathy.CHANNEL_INTERFACE + '.TargetHandle'])

    if handle.get_name() == 'stored':
        channel_class = SunshineSubscribeListChannel
    #hacky & tricky
#    elif handle.get_name() == 'publish':
#        channel_class = SunshineSubscribeListChannel

#    elif handle.get_name() == 'publish':
#        channel_class = ButterflyPublishListChannel
#    elif handle.get_name() == 'hide':
#        channel_class = ButterflyHideListChannel
#    elif handle.get_name() == 'allow':
#        channel_class = ButterflyAllowListChannel
#    elif handle.get_name() == 'deny':
#        channel_class = ButterflyDenyListChannel
    else:
        raise TypeError("Unknown list type : " + handle.get_name())
    return channel_class(connection, manager, props)


class SunshineListChannel(
        SunshineChannel,
        telepathy.server.ChannelTypeContactList,
        telepathy.server.ChannelInterfaceGroup):
    "Abstract Contact List channels"

    def __init__(self, connection, manager, props, object_path=None):
        self._conn_ref = weakref.ref(connection)
        telepathy.server.ChannelTypeContactList.__init__(self, connection, manager, props, object_path=None)
        SunshineChannel.__init__(self, connection, props)
        telepathy.server.ChannelInterfaceGroup.__init__(self)
        self._populate(connection)

    def GetLocalPendingMembersWithInfo(self):
        return []

    @async
    def _populate(self, connection):
        added = set()
        local_pending = set()
        remote_pending = set()

        for contact in connection.gadu_client.contacts:
            ad, lp, rp = self._filter_contact(contact)
            if ad or lp or rp:
                handle = SunshineHandleFactory(self._conn_ref(), 'contact',
                        contact.uin, None)
                #capabilities
                self._conn_ref().contactAdded(handle)
                if ad: added.add(handle)
                if lp: local_pending.add(handle)
                if rp: remote_pending.add(handle)
        self._conn_ref().contactAdded(self._conn_ref().GetSelfHandle())
        self.MembersChanged('', added, (), local_pending, remote_pending, 0,
                telepathy.CHANNEL_GROUP_CHANGE_REASON_NONE)

    def _filter_contact(self, contact):
        return (False, False, False)

    def _contains_handle(self, handle):
        members, local_pending, remote_pending = self.GetAllMembers()
        return (handle in members) or (handle in local_pending) or \
                (handle in remote_pending)


class SunshineSubscribeListChannel(SunshineListChannel):
    """Subscribe List channel.

    This channel contains the list of contact to whom the current used is
    'subscribed', basically this list contains the contact for whom you are
    supposed to receive presence notification."""

    def __init__(self, connection, manager, props):
        SunshineListChannel.__init__(self, connection, manager, props)
        self.GroupFlagsChanged(telepathy.CHANNEL_GROUP_FLAG_CAN_ADD |
                telepathy.CHANNEL_GROUP_FLAG_CAN_REMOVE, 0)

    def AddMembers(self, contacts, message):
        logger.info("Subscribe - AddMembers called")
        for h in contacts:
            handle = self._conn.handle(telepathy.constants.HANDLE_TYPE_CONTACT, h)
            contact_xml = ET.Element("Contact")
            ET.SubElement(contact_xml, "Guid").text = str(handle.name)
            ET.SubElement(contact_xml, "GGNumber").text = str(handle.name)
            ET.SubElement(contact_xml, "ShowName").text = str(handle.name)
            ET.SubElement(contact_xml, "Groups")
            c = GaduContact.from_xml(contact_xml)
            self._conn_ref().gadu_client.addContact( c )
            self._conn_ref().gadu_client.notifyAboutContact( c )
            logger.info("Adding contact: %s" % (handle.name))
            self.MembersChanged('', [handle], (), (), (), 0,
                    telepathy.CHANNEL_GROUP_CHANGE_REASON_INVITED)

            #alias and group settings for new contacts are bit tricky
            #try to set alias
            handle.contact.ShowName = self._conn_ref().get_contact_alias(handle.id)
            #and group
            if self._conn_ref().pending_contacts_to_group.has_key(handle.name):
                logger.info("Trying to add temporary group.")
                handle.contact.updateGroups(self._conn_ref().pending_contacts_to_group[handle.name])
            self._conn_ref().contactAdded(handle)
            logger.info("Contact added.")
        self._conn_ref().exportContactsFile()

    def RemoveMembers(self, contacts, message):
        for h in contacts:
            handle = self._conn.handle(telepathy.HANDLE_TYPE_CONTACT, h)
            contact = handle.contact
            self._conn_ref().gadu_client.removeContact(contact, notify=True)
            self.MembersChanged('', (), [handle], (), (), 0,
                    telepathy.CHANNEL_GROUP_CHANGE_REASON_NONE)
        self._conn_ref().exportContactsFile()

    def _filter_contact(self, contact):
        return (True, False, False)

