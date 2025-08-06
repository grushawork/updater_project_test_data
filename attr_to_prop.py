from lxml import etree


PARSE_FILENAME = '/home/user/dikom_robot_nav_ws/src/dikom_robot_nav/description/robot.urdf.xacro'
REPLACE_FILENAME = '/home/user/dikom_robot_nav_ws/src/xacro_updater/xacro_updater/robot.urdf.xacro'

# Live update of current dikom_robot_nav robot description
REPLACE_FILENAME = PARSE_FILENAME

# Parse and update test robot description
# PARSE_FILENAME = REPLACE_FILENAME

INSERT_PROPERTIES_UNDER = '<xacro:property name="drive_type" value="differential"/>'

TAGS = ['chassis', 'wheel', 'lidar', 'camera']
ATTRIBUTES = ['head', 'tail', 'width', 'height', 'x', 'y', 'z', 'roll', 'pitch', 'yaw', 'radius', 'thickness', 'sign']


def parse_target_tags_attrs(filename=None, target_tags=[], target_attrs=[]):
    if not filename:
        filename = '~/example_robot.urdf.xacro'

    tree = etree.parse(filename)
    root = tree.getroot()

    tags_names = []
    for ttag in target_tags:
        for tag in root.findall('.//{http://www.ros.org/wiki/xacro}' + ttag):
            tag_name = tag.get('name')
            tags_names.append(tag_name if tag_name else 'chassis')
    
    tags_attrs = {tag_name: {} for tag_name in tags_names}

    for tag_name, attrs in tags_attrs.items():
        tag = root.find(f'.//{{http://www.ros.org/wiki/xacro}}*[@name="{tag_name}"]')
        # Костыль для шасси
        if tag_name == 'chassis':
            tag = root.find(f'.//{{http://www.ros.org/wiki/xacro}}chassis')
        
        for attr_name in target_attrs:
            attr_value = tag.get(attr_name)
            if attr_value:
                attrs[attr_name] = attr_value

    return tags_attrs


def formulate_properties(tags_attrs):
    properties_strings = []
    properties = []

    for tag_name, attrs in tags_attrs.items():
        for attr_name, attr_value in attrs.items():
            properties.append({'name': f'{tag_name}_{attr_name}', 'value': attr_value})
            properties_strings.append(f'<xacro:property name="{tag_name}_{attr_name}" value="{attr_value}"/>')

    return properties, properties_strings


def insert_properties(properties, filename, insert_under):
    if not filename:
        filename = '~/example_robot.urdf.xacro'

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if insert_under in line:
            for property in properties[::-1]:
                lines.insert(i + 1, f'\n\t{property}')
            break

    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)


    # for property in properties[::-1]:
    #     tree = etree.parse(filename)
    #     root = tree.getroot()

    #     drive_type = root.find(f".//{{http://www.ros.org/wiki/xacro}}*[@name='drive_type']")
    #     new_property = etree.Element("xacro:property", name=property['name'], value=property['value'])
    #     drive_type.addnext(new_property)

    #     tree.write(filename, pretty_print=True, xml_declaration=True, encoding='UTF-8')


def update_attr_value_by_tag(xml_file, tag_name, attr_name, new_value):
    tree = etree.parse(xml_file)
    root = tree.getroot()

    property = root.find(f".//{{http://www.ros.org/wiki/xacro}}*[@name='{tag_name}']")
    # Костыль для шасси
    if tag_name == 'chassis':
        property = root.find(f".//{{http://www.ros.org/wiki/xacro}}chassis")
    
    if property is not None:
        property.set(attr_name, new_value)
        tree.write(xml_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')


def replace_values_with_properties(tags_attrs, filename):
    for tag_name, attrs in tags_attrs.items():
        for attr_name, _ in attrs.items():
            update_attr_value_by_tag(filename, tag_name, attr_name, f'${{{tag_name}_{attr_name}}}')


if __name__ == '__main__':
    tags_attrs = parse_target_tags_attrs(PARSE_FILENAME, TAGS, ATTRIBUTES)

    properties, properties_strings = formulate_properties(tags_attrs)
    for p in properties_strings:
        print(p)
    
    replace_values_with_properties(tags_attrs, REPLACE_FILENAME)

    insert_properties(properties_strings, REPLACE_FILENAME, INSERT_PROPERTIES_UNDER)
