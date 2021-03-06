from leapp.actors import Actor
from leapp.models import FirewalldFacts
from leapp.tags import FactsPhaseTag, IPUWorkflowTag

from leapp.libraries.actor import private

import os
import xml.etree.ElementTree as ElementTree


class FirewalldFactsActor(Actor):
    """
    Provide data about firewalld

    After collecting data, a message with relevant data will be produced.
    """

    name = 'firewalld_facts_actor'
    consumes = ()
    produces = (FirewalldFacts,)
    tags = (FactsPhaseTag, IPUWorkflowTag)

    def process(self):
        facts = FirewalldFacts()

        try:
            tree = ElementTree.parse('/etc/firewalld/lockdown-whitelist.xml')
            root = tree.getroot()
            facts.firewall_config_command = private.getLockdownFirewallConfigCommand(root)
        except IOError:
            pass

        try:
            tree = ElementTree.parse('/etc/firewalld/direct.xml')
            root = tree.getroot()
            facts.ebtablesTablesInUse = private.getEbtablesTablesInUse(root)
        except IOError:
            pass

        ipsetTypesInUse = set()
        directory = '/etc/firewalld/ipsets'
        try:
            for file in os.listdir(directory):
                if not file.endswith('.xml'):
                    continue
                try:
                    tree = ElementTree.parse(os.path.join(directory, file))
                    root = tree.getroot()
                    ipsetTypesInUse |= set(private.getIpsetTypesInUse(root))
                except IOError:
                    pass
            facts.ipsetTypesInUse = list(ipsetTypesInUse)
        except OSError:
            pass

        self.produce(facts)
