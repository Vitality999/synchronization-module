import pytest
from sync_config import config

host = config.get('oracle').get('host')
pwd = config.get('oracle').get('pwd')
sid = config.get('oracle').get('sid')
port = config.get('oracle').get('port')
user = config.get('oracle').get('user')

def testing_config (host, pwd, sid, port, user):
    assert host == '185.188.183.220'
    assert pwd == 'oracle'
    assert sid == 'xe'
    assert port == '1521'
    assert user == 'system'
testing_config(host, pwd, sid, port, user)
