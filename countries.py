file_name = 'test.txt'
new_file = 'countries.txt'

with open(file_name) as file_object: 
    s = []
    lines = file_object.readlines()
    for line in lines:
        new_line = "'{}': '{}',\n".format(line[3: len(line)-1], line[0:2])
        s.append(new_line)
    

with open(new_file, 'w') as file_object2: 
    for line in s: 
        file_object2.write(line)