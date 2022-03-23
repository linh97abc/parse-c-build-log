import os
import sys
import re


build_log_file = sys.argv[1]

if not os.path.exists(build_log_file):
    raise FileNotFoundError(build_log_file)

info_build_bsp_re = r"^Info: Building\s+([\w\.-_/\\]+)$"
build_complete_re = r"^\[([\w-_\.]+) build complete\]"
link_re = r"^Info: Linking\s+([\w\.-_/\\]+)$"
# compile_re = r"^nios2-elf-gcc[\s.]+\s+-c"

bsp_folder = ''

list_bsp = []
bsp_compile_flag = ''
bsp_defines = []
bsp_includes = []

list_app = []
app_compile_flag = ''
app_defines = []
app_includes = []

linker_flags = ''
exe_file = ''

with open(build_log_file, 'r') as f:
    bsp_building = False
    linking = False
    for line in f:
        if line.startswith("Info:"):
            s = re.findall(info_build_bsp_re, line)
            if s:
                bsp_folder = s[0]
                bsp_building = True
                continue
            s = re.findall(link_re, line)
            if s:
                linking = True
                exe_file = s[0]
        elif "[BSP build complete]\n" == line:
            bsp_building = False
        elif line.startswith("nios2-elf-gcc"):
            cmd = line.split(' ')[1:]
            if '-c' in cmd:
                is_output_arg = False
                output_file = ''
                compile_file = ''
                compile_args = []
                include_paths = []
                defines = []
                compile_flags = []
                for i in cmd:
                    if i == '-o':
                        is_output_arg = True
                    elif not i.startswith('-'):
                        if is_output_arg:
                            output_file = i.replace('\n', '')
                            is_output_arg = False
                        else:
                            compile_file = i.replace('\n', '')
                    elif not i.startswith('-o'):
                        compile_args.append(i)
                
                for i in compile_args:
                    if i.startswith('-I'):
                        include_paths.append(i[2:])
                    elif i.startswith('-D'):
                        defines.append(i[2:])
                    else:
                        compile_flags.append(i)
                
                if bsp_building:
                    list_bsp.append((compile_file, output_file))
                    bsp_defines = defines
                    bsp_compile_flag = ' '.join(compile_flags)
                    bsp_includes = include_paths
                else:
                    list_app.append((compile_file, output_file))
                    app_defines = defines
                    app_compile_flag = ' '.join(compile_flags)
                    app_includes = include_paths
        elif linking:
            linking = False
            cmd = line.split()[1:]
            is_output_arg = False
            linker_args = []
            for i in cmd:
                if i[0] == '-' and not i.startswith('-o'):
                    linker_args.append(i)
            linker_flags = ' '.join(linker_args)


import json

with open("build-import.json", 'w') as f:
    json.dump({
        "bsp_folder": bsp_folder,
        "list_bsp": list_bsp,
        "bsp_defines": bsp_defines,
        "bsp_compile_flag": bsp_compile_flag,
        "bsp_includes": bsp_includes,
        "bsp_includes": bsp_includes,
        "app_defines": app_defines,
        "app_compile_flag": app_compile_flag,
        "app_includes": app_includes,
        "linker_flags": linker_flags,
        "exe_file": exe_file
    }, f, indent=4)

            # sys.exit()
            # pass