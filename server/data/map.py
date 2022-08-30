import bz2

block = None
width = 50
height = 32
type_indexes = {
    "none": "0",
    "normal": "1",
    "start": "2",
    "finish": "3",
    "killer": "4",
    "fantom": "5",
    "jumper": "6",
    "speed": "7"
}

def map_dumps(blocks):
    dict_blocks = {}
    for b in blocks:
        dict_blocks[f"{b.x}x{b.y}"] = type_indexes[b.type]
    data = ""
    for x in range(width):
        for y in range(height):
            if f"{x}x{y}" in dict_blocks:
                data += dict_blocks[f"{x}x{y}"]
            else:
                data += type_indexes["none"]
    data = f"{width}a{height}a{data}"
    return bz2.compress(data.encode("cp866")).decode("cp866")

def map_dump(blocks,filename):
    file = open(filename,"w",encoding="cp866")
    file.write(map_dumps(blocks))
    file.close()

def map_loads(data):
    try:
        data = bz2.decompress(data.encode("cp866")).decode("cp866")
        data = data.split("a")
        width = int(data[0])
        height = int(data[1])
        data = data[2]
        blocks = []
        i = 0
        for x in range(width):
            for y in range(height):
                if data[i] != type_indexes["none"]:
                    blocks.append(block([x,y],list(type_indexes.keys())[list(type_indexes.values()).index(data[i])]))
                i += 1
        return blocks
    except Exception as e:
        print(e)
        return empty_map()

def map_load(filename):
    try:
        file = open(filename,"r",encoding="cp866")
        content = map_loads(file.read())
        file.close()
        return content
    except Exception as e:
        print(e)
        return empty_map()

def empty_map():
    return [block((0,0),"start"),block((784,496),"finish")]
