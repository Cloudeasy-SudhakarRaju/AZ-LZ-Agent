import yaml

def validate_architecture(yaml_file):
    with open(yaml_file) as f:
        kb = yaml.safe_load(f)
    errors = []
    for comp in kb['patterns'][0]['components']:
        if comp['name'] == 'sql_db':
            if comp['config'].get('public_access', False):
                errors.append("SQL DB exposed to public internet!")
        if comp['name'] == 'vnet':
            if comp['config'].get('ddos_protection', False) and kb['patterns'][0]['inputs']['compliance'] != 'high':
                errors.append("DDoS enabled but compliance is not high.")
    # Add more rules as required
    return errors

if __name__ == "__main__":
    errs = validate_architecture("knowledge-base.yml")
    if errs:
        print("Validation Errors:")
        for e in errs:
            print("-", e)
    else:
        print("Validation Passed.")