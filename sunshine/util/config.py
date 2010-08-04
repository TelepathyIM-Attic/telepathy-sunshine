import os
import logging

import xml.etree.ElementTree as ET

__all__ = ['SunshineConfig']

logger = logging.getLogger('Sunshine.Config')

class SunshineConfig(object):
    def __init__(self, uin):
        self.uin = uin
        self.path = None
        self.contacts_count = 0

        self.contacts_len = 0
        self.groups_len = 0

    def make_contacts_file(self, groups, contacts):
        contactbook_xml = ET.Element("ContactBook")

        groups_xml = ET.SubElement(contactbook_xml, "Groups")
        contacts_xml = ET.SubElement(contactbook_xml, "Contacts")

        for group in groups:
            #Id, Name, IsExpanded, IsRemovable
            self.groups_len += 1
            group_xml = ET.SubElement(groups_xml, "Group")
            ET.SubElement(group_xml, "Id").text = group.Id
            ET.SubElement(group_xml, "Name").text = group.Name
            ET.SubElement(group_xml, "IsExpanded").text = str(group.IsExpanded).lower()
            ET.SubElement(group_xml, "IsRemovable").text = str(group.IsRemovable).lower()

        for contact in contacts:
            #Guid, GGNumber, ShowName. MobilePhone. HomePhone, Email, WWWAddress, FirstName, LastName, Gender, Birth, City, Province, Groups, CurrentAvatar, Avatars
            self.contacts_len += 1
            contact_xml = ET.SubElement(contacts_xml, "Contact")
            ET.SubElement(contact_xml, "Guid").text = contact.Guid
            ET.SubElement(contact_xml, "GGNumber").text = contact.GGNumber
            ET.SubElement(contact_xml, "ShowName").text = contact.ShowName
            contact_groups_xml = ET.SubElement(contact_xml, "Groups")
            contact_groups = ET.fromstring(contact.Groups)
            if contact.Groups:
                for group in contact_groups.getchildren():
                    ET.SubElement(contact_groups_xml, "GroupId").text = group.text
            contact_avatars_xml = ET.SubElement(contact_xml, "Avatars")
            ET.SubElement(contact_avatars_xml, "URL").text = ""
            ET.SubElement(contact_xml, "FlagNormal").text = "true"

        main_xml = ET.ElementTree(contactbook_xml)
        if self.contacts_len >= 0 and self.groups_len >= 0:
            return main_xml

    def get_contacts_count(self):
        return self.contacts_count

