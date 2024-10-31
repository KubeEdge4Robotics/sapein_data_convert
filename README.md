# sapein_data_convert

核心改动如下

## 基础格式改动以保证ROS可以加载

1. 将原始的`mobility.urdf`改成`mobility.urdf.xacro`，这一步不是必须得，但是因为后面定义的缩放系数是一个宏，建议转换成`xacro`;
2. 为了保证宏可以生效，在`robot`字段中加入命名空间`xmlns:xacro="http://wiki.ros.org/xacro"`;
3. 定义宏`<xacro:property name="scale" value="100" />`，具体数值，可以在代码中设置；
4. 对于类型为`revolute`或者`prismatic`类型的joint，在`limit`字段中缺少`effort`和`veloity`标签，加载会报错(在ubuntu20，ros noetic上测试)，因此加上对应的标签;
5. 调整mesh文件的路径；

根据以上改动，使用`launch`下面的文件应该是可以加载sapien中的文件的；

## 缩放改动

1. 将所有`link`中的`visual`和`collision`下面的`origin`中的`xyz`都进行缩放，即原始数值除以缩放参数；
2. 将所有`joint`中的`origin`中的`xyz`都进行缩放，即原始数值除以缩放参数；
3. 如果`joint`类型为`prismatic`，`lower`和`upper`标签需要除以缩放因子；
4. 将所有加载的`mesh`进行缩放；

根据以上改动，资产可以进行缩放。已经在10+中开关和5+中门上进行测试。`urdf`文件中案例可以直接加载。

## 代码使用

### 格式转换

在`sapein_file_process.py`中，`SCALE_VALUE`定义了缩放因子。修改成预期的数值，并执行以下命令。
```
# cd到对应的目录
python sapein_file_process.py
```
该代码会遍历urdf下面所有的文件夹，并对其中的文件进行改动。所以可以把所有的sapien资产放入urdf文件夹，批量处理即可；

### 可视化

使用以下命令进行资产的可视化
```
cd sapien_data_convert
source devel/setup.bash
roslaunch data_convert display.launch id:100367  # 最后的数值代表sapien对应的资产编号，确保已经在urdf文件下面了
```