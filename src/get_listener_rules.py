from typing import List

import boto3


def _get_raw_listener_rules(listener_arns: List[str]):
    
    elb = boto3.client('elbv2')

    raw_rules = []
    for la in listener_arns:
        response = elb.describe_rules(ListenerArn=la)


        for rule in response['Rules']:
            raw_rules.append(rule)
    return raw_rules

def get_target_group_mapping(listener_arns: List[str]):
    rules = _get_raw_listener_rules(listener_arns=listener_arns)
    
    
    # get all rules with targets
    target_list = set(filter(None, [
        r['Actions'][0].get('TargetGroupArn')
        for r in rules        
    ]))
    
    # instantiate targets dict
    targets_dict = {
        t : []
        for t in target_list
    }
    
    # assign values to targets
    for t in targets_dict.keys():
        for r in rules:
            if t == r['Actions'][0].get('TargetGroupArn'):
                try:
                    targets_dict[t].extend(r['Conditions'][0].get('Values'))
                except IndexError:
                    continue
    
    clean_targets_dict = {
        k.split('/')[1] : v
        for k,v in targets_dict.items()
    }
                
        
    return clean_targets_dict

