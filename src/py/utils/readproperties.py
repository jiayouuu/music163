from configparser import ConfigParser
#解析properties文件
def read_all(properties_path,section):
    parser=ConfigParser()
    parser.read(properties_path,encoding='utf-8')
    result=parser.items(section=section)
    return dict(result)
def read_one(properties_path,section,option):
    parser=ConfigParser()
    parser.read(properties_path,encoding='utf-8')
    result=parser.get(section=section,option=option)
    return result