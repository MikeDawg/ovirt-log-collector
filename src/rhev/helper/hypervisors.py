"""This module uses the REST API to get a collection of information about hypervisors"""
import logging
import urllib2
import base64
import threading
from ovirtsdk.api import API
from ovirtsdk.xml import params

class ENGINETree(object):

    class DataCenter(object):

        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.clusters = set()

        def add_cluster(self, cluster):
            self.clusters.add(cluster)

        def __str__(self):
            return self.name

    class Cluster(object):

        def __init__(self, id, name):
            self.id = id
            self.name = name
            self.hosts = set()

        def add_host(self, host):
            self.hosts.add(host)

        def __str__(self):
            return self.name

    class Host(object):

        def __init__(self, address, name=None):
            self.address = address
            self.name = name

        def __str__(self):
            return self.address

    def __init__(self):
        self.datacenters = set()
        self.clusters = set()
        self.hosts = set()

    def add_datacenter(self, datacenter):
        dc_obj = self.DataCenter(datacenter.id, datacenter.name)
        self.datacenters.add(dc_obj)

    def add_cluster(self, cluster):
        c_obj = self.Cluster(cluster.id, cluster.name)
        self.clusters.add(c_obj)
        if cluster.get_data_center() is not None:
            for dc in self.datacenters:
                if dc.id == cluster.get_data_center().id:
                    dc.add_cluster(c_obj)
        else:
            dummySeen = 0
            for dc in self.datacenters:
                if dc.id == "":
                    dc.add_cluster(c_obj)
                    dummySeen = 1
            if dummySeen == 0:
                dc = self.DataCenter("", "")
                dc.add_cluster(c_obj)
                self.datacenters.add(dc)

    def add_host(self, host):
        host_obj = self.Host(host.get_address(), host.name)
        self.hosts.add(host_obj)
        if host.get_cluster() is not None:
            for cluster in self.clusters:
                if cluster.id == host.get_cluster().id:
                    cluster.add_host(host_obj)
        else:
            dummySeen = 0
            for cluster in self.clusters:
                if cluster.id == "":
                    cluster.add_host(host_obj)
                    dummySeen = 1
            if dummySeen == 0:
                c_obj = self.Cluster("", "")
                c_obj.add_host(host_obj)
                self.clusters.add(c_obj)
                dc = self.DataCenter("", "")
                dc.add_cluster(c_obj)
                self.datacenters.add(dc)

    def __str__(self):
        return "\n".join(["%-20s | %-20s | %s" % (dc, cluster, host)
                            for dc in self.datacenters
                            for cluster in dc.clusters
                            for host in cluster.hosts])

    def get_sortable(self):
        return [(dc.name, cluster.name, host.address)
                    for dc in self.datacenters
                    for cluster in dc.clusters
                    for host in cluster.hosts]


def _initialize_api(hostname, username, password):
    """
    Initialize the oVirt RESTful API
    """
    url = "https://" + hostname + "/api"
    api = API(url=url,
              username=username,
              password=password)
    try:
        pi = api.get_product_info()
        if pi is not None:
            vrm = '%s.%s.%s' % (pi.get_version().get_major(),
                                pi.get_version().get_minor(),
                                pi.get_version().get_revision())
            logging.debug("API Vendor(%s)\tAPI Version(%s)" %  (pi.get_vendor(), vrm))
        else:
            logging.error(_("Unable to connect to REST API."))
            return None
    except Exception, e:
        logging.error(_("Unable to connect to REST API.  Message: %s") %  e)
        return None
    return api

def get_all(hostname, username, password):

    tree = ENGINETree()

    try:
        api = _initialize_api(hostname, username, password)
        if api is not None:
            for dc in api.datacenters.list():
                tree.add_datacenter(dc)
            for cluster in api.clusters.list():
                tree.add_cluster(cluster)
            for host in api.hosts.list():
                tree.add_host(host)
            return set(tree.get_sortable())
    except Exception, e:
        logging.error(_("Failure fetching information about hypervisors from API . Error: %s") % e)

    return set()

