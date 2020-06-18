"""
Description : Example of using Drain3 with Kafka persistence
Author      : David Ohana, Moshik Hershcovitch, Eran Raichstein
Author_email: david.ohana@ibm.com, moshikh@il.ibm.com, eranra@il.ibm.com
License     : MIT
"""
import configparser
import json
import logging
import sys
sys.path.append('../')

from logparsing.drain.drain3.template_miner import TemplateMiner
from logparsing.drain.drain3.file_persistence import FilePersistence

persistence_type = "FILE"

config = configparser.ConfigParser()
config.read('drain3.ini')

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')
persistence = FilePersistence("drain3_state.bin")
template_miner = TemplateMiner(persistence)
print(f"Drain3 started with '{persistence_type}' persistence, reading from std-in (input 'q' to finish)")
while True:
    log_line = input()
    if log_line == 'q':
        break
    result = template_miner.add_log_message(log_line)
    result_json = json.dumps(result)
    print(result_json)

print("Clusters:")
for cluster in template_miner.drain.clusters:
    print(cluster)
