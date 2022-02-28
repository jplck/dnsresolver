import logging
import os
import sys
import json
import datetime
import dns.update
import dns.query
import dns.tsigkeyring
import dns.reversename
import dns.resolver
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
import azure.mgmt.resource
from azure.identity import ChainedTokenCredential,ManagedIdentityCredential
from dotenv import load_dotenv

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    load_dotenv()
    
    #------------------------------------- Read in all of the input from the WEBHOOK parameter
    print ('\n\n ---- Data from WEBHOOKDATA --------')

    # Parse body as json string
    in_RequestBody = req.get_json()
    in_alertTargetIDs1=in_RequestBody['data']['essentials']['alertTargetIDs'][0].split('/')
    subscr1=in_alertTargetIDs1[2]
    res_gr1=in_alertTargetIDs1[4]
    vmname1=in_alertTargetIDs1[-1]
    print ('Subscr: '+subscr1)
    print ('Resourcegroup: '+res_gr1)
    print ('VMname: '+vmname1)

    #azure_credential = DefaultAzureCredential()

    MSI_credential = ManagedIdentityCredential()
    credential_chain = ChainedTokenCredential(MSI_credential)

    subscription_id = subscr1

    # Azure Automation API - get IP of VM
    network_client = azure.mgmt.network.NetworkManagementClient(credential_chain, subscription_id)
    compute_client = azure.mgmt.compute.ComputeManagementClient(credential_chain, subscription_id)
    vm1 = compute_client.virtual_machines.get(res_gr1,vmname1)

    for interface in vm1.network_profile.network_interfaces:
        int_name=" ".join(interface.id.split('/')[-1:])
        int_sub="".join(interface.id.split('/')[4])
        ni=network_client.network_interfaces.get(int_sub, int_name).ip_configurations
        #print (ni)
        for x in ni:
            print(vm1.name, x.private_ip_address)  #interface name and private IP
            vmIP1=x.private_ip_address
    #! always only one interface ???

    print ('VMname: '+vmname1)
    print ('VMip: '+vmIP1)

    #------------------------------------- DNS UPDATE - CREATE
    print ('\n\n ---- CREATE-DNS entry --------')

    return func.HttpResponse(
        "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        status_code=200
    )
