import os
import xml.etree.ElementTree as ET

# 定义常量
SCALE_VALUE = '100'  # 方便修改的scale值

def convert_to_xacro_format(value):
    """将数值转换为xacro格式"""
    return f"${{{value} / scale}}"

def process_urdf_file(file_path):
    # 获取文件夹名称
    folder_name = os.path.basename(os.path.dirname(file_path))
    
    # 解析URDF文件
    tree = ET.parse(file_path)
    root = tree.getroot()

    # 1. 修改文件名
    new_file_path = file_path.replace('mobility.urdf', 'mobility.urdf.xacro')

    # 2. 添加xmlns:xacro属性
    root.attrib['xmlns:xacro'] = "http://wiki.ros.org/xacro"

    # 3. 处理joint
    for joint in root.findall('joint'):
        joint_type = joint.attrib['type']
        limit = joint.find('limit')
        if limit is not None and (joint_type == 'revolute' or joint_type == 'prismatic'):
            limit.attrib['effort'] = "10.0"
            limit.attrib['velocity'] = "0.1"

            if joint_type == 'prismatic':
                # 使用原始值替换为xacro格式
                limit.attrib['lower'] = convert_to_xacro_format(limit.attrib['lower'])
                limit.attrib['upper'] = convert_to_xacro_format(limit.attrib['upper'])

        # 处理joint中的origin
        origin = joint.find('origin')
        if origin is not None:
            xyz = origin.attrib['xyz'].split()
            scaled_xyz = [convert_to_xacro_format(coord) for coord in xyz]
            origin.attrib['xyz'] = ' '.join(scaled_xyz)

    # 4. 处理link中的origin和mesh
    for link in root.findall('link'):
        link_name = link.attrib['name']
        if link_name.startswith('base'):
            continue  # 跳过以base开头的link

        for visual in link.findall('visual'):
            origin = visual.find('origin')
            if origin is not None:
                xyz = origin.attrib['xyz'].split()
                scaled_xyz = [convert_to_xacro_format(coord) for coord in xyz]
                origin.attrib['xyz'] = ' '.join(scaled_xyz)

            mesh = visual.find('geometry/mesh')
            if mesh is not None:
                # 更新mesh路径
                new_filename = mesh.attrib['filename'].replace(
                    'textured_objs/', f'package://data_convert/urdf/{folder_name}/textured_objs/'
                )
                mesh.attrib['filename'] = new_filename
                mesh.attrib['scale'] = "${1 / scale} ${1 / scale} ${1 / scale}"

        for collision in link.findall('collision'):
            origin = collision.find('origin')
            if origin is not None:
                xyz = origin.attrib['xyz'].split()
                scaled_xyz = [convert_to_xacro_format(coord) for coord in xyz]
                origin.attrib['xyz'] = ' '.join(scaled_xyz)

            mesh = collision.find('geometry/mesh')
            if mesh is not None:
                # 更新mesh路径
                new_filename = mesh.attrib['filename'].replace(
                    'textured_objs/', f'package://data_convert/urdf/{folder_name}/textured_objs/'
                )
                mesh.attrib['filename'] = new_filename
                mesh.attrib['scale'] = "${1 / scale} ${1 / scale} ${1 / scale}"

    # 5. 添加宏定义
    xacro_property = ET.Element('xacro:property', {'name': 'scale', 'value': SCALE_VALUE})
    root.insert(0, xacro_property)

    # 保存到新文件
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(ET.tostring(root, encoding='utf-8').decode('utf-8'))
        f.write('\n')  # 在宏定义后添加换行符

def process_directory(directory):
    for root_dir, _, files in os.walk(directory):
        for file in files:
            if file == 'mobility.urdf':
                file_path = os.path.join(root_dir, file)
                process_urdf_file(file_path)

if __name__ == "__main__":
    # 设置目标目录
    target_directory = './urdf'
    process_directory(target_directory)