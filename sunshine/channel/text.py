# telepathy-sunshine is the GaduGadu connection manager for Telepathy
#
# Copyright (C) 2006-2007 Ali Sabil <ali.sabil@gmail.com>
# Copyright (C) 2007 Johann Prieur <johann.prieur@gmail.com>
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
import time

import telepathy

from sunshine.util.decorator import async, escape
from sunshine.handle import SunshineHandleFactory
from sunshine.channel import SunshineChannel

__all__ = ['SunshineTextChannel']

logger = logging.getLogger('Sunshine.TextChannel')


class SunshineTextChannel(SunshineChannel,
                          telepathy.server.ChannelTypeText,
                          telepathy.server.ChannelInterfaceChatState):

    def __init__(self, conn, manager, conversation, props, object_path=None):
        _, surpress_handler, handle = manager._get_type_requested_handle(props)
        self._recv_id = 0
        self._conn_ref = weakref.ref(conn)
        self.conn = conn

        self.handle = handle
        telepathy.server.ChannelTypeText.__init__(self, conn, manager, props, object_path=None)
        SunshineChannel.__init__(self, conn, props)
        telepathy.server.ChannelInterfaceChatState.__init__(self)

    def Send(self, message_type, text):
        if message_type == telepathy.CHANNEL_TEXT_MESSAGE_TYPE_NORMAL:
            logger.info("Sending message to %s, id %s, body: '%s'" % (str(self.handle.name), str(self.handle.id), unicode(text)))
            msg = text.decode('UTF-8').encode('windows-1250', 'replace')
            #gg_text = escape(text.decode('UTF-8')).encode('UTF-8').replace('<', '&lt;').replace('>', '&gt;')
            gg_text = text.decode('UTF-8', 'xmlcharrefreplace').replace('<', '&lt;').replace('>', '&gt;')
            self._conn_ref().profile.sendTo(int(self.handle.name), str(gg_text), str(msg))
            self._conn_ref().profile.sendTypingNotify(int(self.handle.name), 0)
        else:
            raise telepathy.NotImplemented("Unhandled message type")
        self.Sent(int(time.time()), message_type, text)

    def Close(self):
        telepathy.server.ChannelTypeText.Close(self)
        self.remove_from_connection()

    # Redefine GetSelfHandle since we use our own handle
    #  as Butterfly doesn't have channel specific handles
    def GetSelfHandle(self):
        return self._conn.GetSelfHandle()

    # Rededefine AcknowledgePendingMessages to remove offline messages
    # from the oim box.
    def AcknowledgePendingMessages(self, ids):
        telepathy.server.ChannelTypeText.AcknowledgePendingMessages(self, ids)
#        messages = []
#        for id in ids:
#            if id in self._pending_offline_messages.keys():
#                messages.append(self._pending_offline_messages[id])
#                del self._pending_offline_messages[id]
#        self._oim_box_ref().delete_messages(messages)

    # Rededefine ListPendingMessages to remove offline messages
    # from the oim box.
    def ListPendingMessages(self, clear):
        return telepathy.server.ChannelTypeText.ListPendingMessages(self, clear)

    def SetChatState(self, state):
        # Not useful if we dont have a conversation.
        if state == telepathy.CHANNEL_CHAT_STATE_COMPOSING:
            t = 1
        else:
            t = 0

        handle = SunshineHandleFactory(self._conn_ref(), 'self')
        self._conn_ref().profile.sendTypingNotify(int(self.handle.name), t)
        self.ChatStateChanged(handle, state)

class SunshineRoomTextChannel(telepathy.server.ChannelTypeText, telepathy.server.ChannelInterfaceGroup):

    def __init__(self, conn, manager, conversation, props, object_path=None):
        _, surpress_handler, handle = manager._get_type_requested_handle(props)
        self._recv_id = 0
        self._conn_ref = weakref.ref(conn)
        self.conn = conn

        if conversation != None:
            self.contacts = conversation

        self.handle = handle
        telepathy.server.ChannelTypeText.__init__(self, conn, manager, props, object_path=None)
        telepathy.server.ChannelInterfaceGroup.__init__(self)

        self.GroupFlagsChanged(telepathy.CHANNEL_GROUP_FLAG_CAN_ADD, 0)

    def Send(self, message_type, text):
        if message_type == telepathy.CHANNEL_TEXT_MESSAGE_TYPE_NORMAL:
            recipients = []
            if self.contacts != None:
                for rhandle in self.contacts:
                    recipients.append(rhandle.name)

            for nr in recipients:
                print nr
                recs_tmp = sorted(recipients)
                recs_tmp.remove(nr)

                logger.info("Sending message to %s, id %s, body: '%s'" % (str(nr), str(self.handle.id), unicode(text)))
                msg = text.encode('windows-1250')
                self.conn.gadu_client.sendToConf(int(nr), str(text), str(msg), recs_tmp)
        else:
            raise telepathy.NotImplemented("Unhandled message type")
        self.Sent(int(time.time()), message_type, text)

    def Close(self):
        telepathy.server.ChannelTypeText.Close(self)
        self.remove_from_connection()

    # Redefine GetSelfHandle since we use our own handle
    #  as Butterfly doesn't have channel specific handles
    def GetSelfHandle(self):
        return self._conn.GetSelfHandle()

    # Rededefine AcknowledgePendingMessages to remove offline messages
    # from the oim box.
    def AcknowledgePendingMessages(self, ids):
        telepathy.server.ChannelTypeText.AcknowledgePendingMessages(self, ids)
#        messages = []
#        for id in ids:
#            if id in self._pending_offline_messages.keys():
#                messages.append(self._pending_offline_messages[id])
#                del self._pending_offline_messages[id]
#        self._oim_box_ref().delete_messages(messages)

    def ListPendingMessages(self, clear):
        return telepathy.server.ChannelTypeText.ListPendingMessages(self, clear)

    def getContacts(self, contacts):
        self.contacts = contacts

#        if clear:
#            messages = self._pending_offline_messages.values()
#            self._oim_box_ref().delete_messages(messages)
#        return telepathy.server.ChannelTypeText.ListPendingMessages(self, clear)


