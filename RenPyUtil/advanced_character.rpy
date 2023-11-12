# 此文件提供了一系列基于Ren'Py的功能类，以供Ren'Py开发者调用
# 作者  ZYKsslm
# 仓库  https://github.com/ZYKsslm/RenPyUtil
# 声明  该源码使用 MIT 协议开源，但若使用需要在程序中标明作者信息


init -1 python:


    import random

    NotSet = renpy.object.Sentinel("NotSet")
    class AdvancedCharacter(ADVCharacter):
        """该类继承自ADVCharacter类，在原有的基础上增添了一些新的属性和方法。"""

        def __init__(self, name=NotSet, kind=None, **properties):
            """初始化方法。若实例属性需要被存档保存，则定义对象时请使用`default`语句或Python语句。

            Keyword Arguments:
                name -- 角色名。 (default: {NotSet})
                kind -- 角色类型。 (default: {None})
            """

            super().__init__(name, kind=kind, **properties)
            self.task_list = []
            self.task_return_dict = {}
            self.customized_attr_dict = {}

        def add_attr(self, attr_dict: dict = None, **attrs):
            """调用该方法，给该角色对象创建自定义的一系列属性。

            Keyword Arguments:
                attr_dict -- 一个键为属性名，值为属性值的字典。若该参数不填，则传入参数作为属性名，参数值作为属性值。 (default: {None})

            Example:
                character.add_attr(strength=100, health=100)
                character.add_attr(attr_dict={strength: 10, health: 5})
            """

            attr = attr_dict if attr_dict else attrs

            for a, v in attr.items():
                setattr(self, a, v)
                self.customized_attr_dict[a] = v

        def set_task(self, task_name, attr_pattern: dict, func_dict: dict[function: tuple], run_in_new_thread=False):
            """调用该方法，创建一个任务，将一个函数与一个或多个自定义属性绑定，当自定义属性变成指定值时执行绑定函数。

            若函数被执行，则函数的返回值储存在实例属性`self.task_return_dict`中。其中键为任务名，值为一个返回值列表。
            当任务函数在新线程中运行时无法获得返回值。

            Arguments:
                task_name -- 任务名。
                attr_pattern -- 一个键为自定义属性的字典。当该角色对象的自定义属性变成字典中指定的值时执行绑定函数。
                func_dict -- 一个键为函数，值为一个参数元组的字典。

            Keyword Arguments:
                run_in_new_thread -- 若为True，则任务函数在新线程中运行 (default: {False})
            """            

            self.task_list.append([task_name, attr_pattern, func_dict, run_in_new_thread])

        def set_attr(self, attr, value):
            """调用该方法，修改一个自定义属性的值。若没有该属性则创建一个。

            Arguments:
                attr -- 自定义属性名。
                value -- 要赋予的值。
            """

            setattr(self, attr, value)
            self.customized_attr_dict[attr] = value

        def __setattr__(self, key, value):
            super().__setattr__(key, value)

            # 跳过初始化属性赋值阶段
            # 跳过非自定义属性
            if (not hasattr(self, "customized_attr_dict")) or (not key in self.customized_attr_dict.keys()):
                return

            for task in self.task_list:
                task_name, attr_pattern, func_dict, run_in_new_thread = task

                for attr, value in attr_pattern.items():
                    if getattr(self, attr) != value:
                        return
                
                func_return_list = []
                for func, args in func_dict.items():
                    if run_in_new_thread:
                        renpy.invoke_in_thread(func, *args)
                    else:
                        func_return = func(*args)
                        func_return_list.append(func_return)
                
                if func_return_list:
                    self.task_return_dict.update(
                        {
                            task_name: func_return_list
                        }
                    )

        def get_customized_attr(self):
            """调用该方法，返回一个键为自定义属性，值为属性值的字典，若无则为空字典。

            Returns:
                个键为自定义属性，值为属性值的字典。
            """

            return self.customized_attr_dict


    class CharacterError(Exception):
        """该类为一个异常类，用于检测角色对象。"""

        errorType = {
            0: "错误地传入了一个ADVCharacter类，请传入一个AdvancedCharacter高级角色类！",
            1: "传入对象类型异常，请传入一个AdvancedCharacter高级角色类！"
        }

        def __init__(self, *args: object):
            super().__init__(args)
            self.errorCode = None

        def check(self, obj):

            if isinstance(obj, AdvancedCharacter):
                return
            elif (not isinstance(obj, AdvancedCharacter)) and (isinstance(obj, ADVCharacter)):
                self.errorCode = 0
            else:
                self.errorCode = 1
            raise self

        def __str__(self):
            return CharacterError.errorType[self.errorCode]


    class CharacterGroup(object):
        """该类用于管理多个高级角色（AdvancedCharacter）对象。"""

        def __init__(self, *characters: AdvancedCharacter):
            """初始化方法。"""

            self.type_checker = CharacterError()
            self.character_group = list(characters)

            # 检查角色组中对象类型
            for obj in self.character_group:
                self.type_checker.check(obj)

        def get_random_character(self):
            """调用该方法，返回角色组中随机一个角色对象。"""

            character = random.choice(self.character_group)
            return character

        def del_character(self, character):
            """调用该方法，删除角色组中的一个角色对象。

            Arguments:
                character -- 要删除的角色对象。
            """

            self.character_group.remove(character)

        def add_group_attr(self, attr_dict: dict = None, **attrs):
            """调用该方法，对角色组中所有角色对象创建自定义的一系列属性。

            Keyword Arguments:
                attr_dict -- 一个键为属性名，值为属性值的字典。若该参数不填，则传入参数作为属性名，参数值作为属性值。 (default: {None})

            Example:
                character_group.add_group_attr(strength=100, health=100)
                character_group.add_group_attr(attr_dict={strength: 10, health: 5})
            """

            attr = attr_dict if attr_dict else attrs

            for character in self.character_group:
                character.add_attr(attr)

        def set_group_attr(self, attr, value):
            """调用该方法，更改角色组中所有角色对象的一项自定义属性值。若没有该属性，则创建一个。

            Arguments:
                attr -- 自定义属性名。
                value -- 自定义属性值。
            """

            for character in self.character_group:
                character.set_attr(attr, value)
        
        def set_group_func(self, task_name, attr_pattern: dict, func_dict: dict[function: dict]):
            """调用该方法，给所有角色组中的角色对象创建一个任务，将一个函数与一个或多个自定义属性绑定，当自定义属性变成指定值时执行绑定函数。
            若函数被执行，则函数的返回值储存在对象的实例属性`self.task_return_dict`中。其中键为任务名，值为一个返回值列表。

            Arguments:
                task_name -- 任务名。
                attr_pattern -- 一个键为自定义属性的字典。当该角色对象的自定义属性变成字典中指定的值时执行绑定函数。
                func_dict -- 一个键为函数，值为一个参数字典的字典。
            """

            for character in self.character_group:
                character.set_task(task_name, attr_pattern, func_dict)