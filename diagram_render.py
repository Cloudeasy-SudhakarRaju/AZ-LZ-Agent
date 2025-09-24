import yaml

def generate_plantuml(yaml_file):
    with open(yaml_file) as f:
        kb = yaml.safe_load(f)
    plantuml_code = "@startuml\n"
    for comp in kb['patterns'][0]['components']:
        visual = comp.get("visual", {})
        plantuml_code += f'component "{comp["name"]}" as {comp["name"]} <<{visual.get("icon", "")}> > #line:{visual.get("color", "#fff")}\n'
    for rel in kb['patterns'][0]['relationships']:
        visual = rel.get("visual", {})
        style = visual.get("line_style", "solid")
        plantuml_code += f'{rel["from"]} --> {rel["to"]} : {rel["type"]} [{style}]\n'
    plantuml_code += "@enduml"
    return plantuml_code

if __name__ == "__main__":
    code = generate_plantuml("knowledge-base.yml")
    print(code)
    # Integration with PlantUML server or Draw.io API goes here
