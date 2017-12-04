#!/bin/env python2.6
import os
import urllib
import urllib2
import sys
import fcntl
import string
import json
import zabbix_proxy_balancer_config as config

#Define to connect into server and send json payload
def connect(data):
    data_json = json.dumps(data)
    url = 'http://%s/zabbix/api_jsonrpc.php' %(config.connect['server'])
    payload = urllib2.Request(url, data_json, {'Content-Type': 'application/json'})
    res = urllib2.urlopen(payload)
    response = res.read()
    return response

# Zabbix store Token
def get_token():
    token = json.loads(connect({ "jsonrpc":"2.0","method":"user.login","params":{"user": config.login['user'] ,"password": config.login['password']}, "id":"1" }))['result']
    return token

def get_zabbix_best_proxy(token):
    proxy_list = {}
    best_proxy = ""
    group_id = json.loads(connect({"jsonrpc": "2.0","method": "hostgroup.get","params": {"output": "extend","filter" : {"name": config.group['name']}},"auth": token,"id":"1"}))['result'][0]['groupid']
    ans = json.loads(connect({"jsonrpc": "2.0","method": "hostgroup.get","params": {"groupids": group_id,"output": "extend","selectHosts":""},"auth": token,"id":"1"}))['result']
    for item in ans:
        hosts = item['hosts']
        for host_item in hosts:
            hostid = host_item['hostid']
            raw_value = json.loads(connect({"jsonrpc": "2.0","method": "item.get","params": {"hostids": hostid,"output": "extend"},"auth": token,"id":"1"}))['result']
            for item in raw_value:
                name = item['name']
                if name == "Values processed by Zabbix proxy per second":
                    raw_value = item['lastvalue']
                    value = raw_value.replace(".", "")
                    proxy_list.update({json.loads(hostid):json.loads(value)})
    best_proxy_id = min(proxy_list, key=proxy_list.get)
    best_proxy = json.loads(connect({"jsonrpc": "2.0","method": "host.get","params": {"hostids": best_proxy_id,"output": "extend"},"auth": token,"id":"1"}))['result'][0]['name']
    print best_proxy
    return best_proxy
