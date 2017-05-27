# coding:UTF-8
import libvirt
import os
import re
import json
from xml.dom import minidom
from kvmconnect.base import BaseReadOnly


class DomainInfo(BaseReadOnly):
    """
    Show VM's information
    """

    def __init__(self):
        super().__init__()

    # Bridge interface's name
    def get_bridge(self, iface):
        iface_type = iface.getAttribute("type")

        if iface_type == "network":
            XML_temp = Conn.networkLookupByName(network_info).XMLDesc(0)
            net_XML_info = minidom.parseString(XML_temp)
            bridge = net_XML_info.getElementsByTagName("bridge")[0].getAttribute("name")

        elif iface_type == "bridge":
            bridge = iface.getElementsByTagName("source")[0].getAttribute("bridge")

        else:
            bridge = None

        return {"bridge": bridge}

    # Network name
    def get_network(self, iface):
        iface_type = iface.getAttribute("type")

        if iface_type == "network":
            network = iface.getElementsByTagName("source")[0].getAttribute("network")
        else:
            network = None

        return {"network": network}

    # Mac address
    def get_mac(self, iface):
        mac = iface.getElementsByTagName("mac")[0].getAttribute("address")
        return {"mac_address": mac}

    # Device(nic) name
    def get_device(self, iface):
        try:
            device = iface.getElementsByTagName("target")[0].getAttribute("dev")
        except IndexError:
            return {"device": "None"}
        return {"device": device}

    # Domain(VM) name
    def get_domain(self, id):
        domain = self.connection.lookupByName(id)
        return {"name": domain.name()}

    # VM tatus
    def get_state(self, id):
        domain = self.connection.lookupByName(id)
        return {"state": domain.info()[0]}

    # VM max memory
    def get_max_memory(self, id):
        domain = self.connection.lookupByName(id)
        return {"max_memory": domain.info()[1]}

    # Number of CPU
    def get_CPU_number(self, id):
        domain = self.connection.lookupByName(id)
        return {"number_of_CPU": domain.info()[3]}

    # CPU time
    def get_CPU_time(self, id):
        domain = self.connection.lookupByName(id)
        return {"CPU_time": domain.info()[2]}

    # Domain's XML(for settings)
    def get_domain_XML(self, id):
        domain = self.connection.lookupByName(id)
        return minidom.parseString(domain.XMLDesc(0))

    def get_domain_list(self):
        # Get stopped domain list
        domain_list = self.connection.listDefinedDomains()

        # Get running domain list
        running_domains = self.connection.listDomainsID()
        if running_domains is None or len(running_domains) == 0:
            pass
        else:
            for id in running_domains:
                domain = self.connection.lookupByID(id)
                domain_list.append(domain.name())

        return {"domain_list": domain_list}

    # All information
    def get_domain_info_all(self):
        domain = []
        domain_names = self.get_domain_list()["domain_list"]
        print(domain_names)

        for name in domain_names:
            dom_info = {"name": name}
            dom_info.update(self.get_domain(name))
            dom_info.update(self.get_state(name))
            dom_info.update(self.get_max_memory(name))
            dom_info.update(self.get_CPU_number(name))
            dom_info.update(self.get_CPU_time(name))

            # Read XML file
            domain_XML = self.get_domain_XML(name)
            networks = []
            # Show interface's information
            for iface in domain_XML.getElementsByTagName("interface"):
                networks.append(self.get_domain_network_info(iface))
            dom_info.update({"networks": networks})
            domain.append(dom_info)

        return {"interfaces": domain}

    # One information
    def get_domain_info(self, name):
        dom_info = {"name": name}
        dom_info.update(self.get_domain(name))
        dom_info.update(self.get_state(name))
        dom_info.update(self.get_max_memory(name))
        dom_info.update(self.get_CPU_number(name))
        dom_info.update(self.get_CPU_time(name))
        
        # Read XML file
        domain_XML = self.get_domain_XML(name)
        networks = []
        # Show interface's information
        for iface in domain_XML.getElementsByTagName("interface"):
            networks.append(self.get_domain_network_info(iface))
        dom_info.update({"networks": networks})

        return dom_info

    # Get network information
    def get_domain_network_info(self, iface):
        network_info = {"interface_type": iface.getAttribute("type")}
        network_info.update(self.get_network(iface))
        network_info.update(self.get_bridge(iface))
        network_info.update(self.get_mac(iface))
        network_info.update(self.get_device(iface))

        return network_info
