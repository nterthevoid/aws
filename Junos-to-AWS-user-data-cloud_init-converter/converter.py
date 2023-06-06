def process_config_file():
    config = input ('Enter the name of the source file to be converted   > ')
    userdata = input ('Enter the name of the converted destination file   > ')
    source_file = config
    output_file = userdata

    with open(source_file, "r") as source:
        lines = source.readlines()

    found_junos_config_statement = False
    with open(output_file, "w") as output:
        output.write('"UserData": {\n')
        output.write('"Fn::Base64": {\n')
        output.write('"Fn::Join": [\n')
        output.write('"')
        output.write("\\n")
        output.write('",\n')
        output.write('[\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("#junos-config"):
                found_junos_config_statement = True
            if found_junos_config_statement:
                if '"' in line:
                    line = line.replace('"', '\\"') 
                modified_line = '"' + line.strip() + '",'
                if i == len(lines) - 1:
                    modified_line = '"' + line.strip() + '"'
                modified_line += "\n"
                output.write(modified_line)
        output.write(']\n')
        output.write(']\n')
        output.write('}\n')
        output.write('},\n')

    print(f"Converted source file [ {source_file} ] and saved it as [ {output_file} ].")


process_config_file()
