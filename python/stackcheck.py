#linux stack check: use objdump -D to dump asm file,and check
from collections import OrderedDict

func_map = OrderedDict()


def build_Path(stack, root, pathlist, recursion_list):
    if root['funcname'] in stack:
        stack.append(root['funcname'])
        save_path(stack, recursion_list)
        save_path(stack, pathlist)
        stack.pop()
        return

    if len(stack) > 50:
        print("too depth stack:", root['funcname'])
        return

    stack.append(root['funcname'])

    if len(root['called_funcs']) == 0:
        save_path(stack, pathlist)
    else:
        for item in root['called_funcs']:
            if not func_map.has_key(item):
                print "func not found:" + item + '\n'
            else:
                build_Path(stack, func_map[item], pathlist, recursion_list)

    stack.pop()


def save_path(path, pathlist):
    paths = []
    for item in path:
        paths.append(item)
    pathlist.append(paths)


def set_max_stacksize(root):
    pathlist = []
    max_stack_size = 0
    recursion_list = []
    stack = []

    build_Path(stack, root, pathlist, recursion_list)

    for paths in pathlist:
        stack_sizes = 0
        # root["stack_list"].append(paths)
        for path in paths:
            stack_sizes += func_map[path]['stack_size']
        if stack_sizes > max_stack_size:
            max_stack_size = stack_sizes
            root["max_path"] = paths

    root["stack_max_size"] = max_stack_size

    if len(recursion_list) > 0:
        root["hava_recursion"] = True
        for paths in recursion_list:
            root["recursion_list"].append(paths)


def get_recursion_func_list():
    func_list = []
    for v in func_map.values():
        if v["hava_recursion"]:
            func_list.append(v["funcname"])
    return func_list


def sort_by_stack_size():
    bar = OrderedDict(sorted(func_map.items(), key=lambda x: x[1]["stack_max_size"], reverse=True))

    print("func name sort by max stack size:name, max_size, stack depth\n")
    for key, value in bar.items():
        if value["stack_max_size"] > 100:
            print (key, value["stack_max_size"], len(value["max_path"]))

    bar1 = OrderedDict(sorted(func_map.items(), key=lambda x: x[1]["stack_size"], reverse=True))

    print("\n\nfunc name sort by stack size:name, sekf stack size\n")
    for key, value in bar1.items():
        if value["stack_size"] > 100:
            print (key, value["stack_size"])

    print("\n\n")
    import json
    print(json.dumps(bar, indent=4))
    print("\n\n")


def parse(filename):
    f = open(filename)
    line = f.readline()
    while line:
        if ">:" in line:
            # print line
            line = process_func(f, line)

        else:
            line = f.readline()
    f.close()


def process_func(f, line):
    fun_name = line.split(">")[0].split("<")[1]
    # print "func: " + fun_name + "\n"
    func_map[fun_name] = {}

    func_map[fun_name]["funcname"] = fun_name
    func_map[fun_name]["stack_size"] = 0
    func_map[fun_name]["called_funcs"] = []
    func_map[fun_name]["stack_max_size"] = 0
    func_map[fun_name]["max_path"] = []
    func_map[fun_name]["hava_recursion"] = False
    func_map[fun_name]["recursion_list"] = []
    func_map[fun_name]["stack_list"] = []

    line = f.readline()
    if not line: return
    while not (">:" in line):
        line = f.readline()
        if not line:
            break
        if "sub" in line and ",%rsp" in line and "$" in line:
            stacksize = line.split("$")[1].split(",")[0]
            if stacksize == "0xffffffffffffff80":
                stacksize = 128
            else:
                stacksize = int(stacksize, 16)
            func_map[fun_name]["stack_size"] = func_map[fun_name]["stack_size"] + stacksize

        if ("callq " in line) or ("call " in line) or ("jmp " in line) or ("jmpq " in line):
            if not "+" in line:
                if "<" in line and ">" in line:
                    call_fun_name = line.split(">")[0].split("<")[1]
                    func_map[fun_name]["called_funcs"].append(call_fun_name)
    return line


if __name__ == '__main__':

    file_list = [r".\\vmlinux.asm\\vmlinux.asm", ]
    
    for file in file_list:
        parse(file)

    '''for v in func_map.values():
        if v["stack_size"] > 500:
            set_max_stacksize(v)'''

    print("\nrecirsion list:\n")
    print(get_recursion_func_list())

    print("\nsorted function list:\n")
    sort_by_stack_size()

    print("\n\n")
