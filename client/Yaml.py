import yaml

def save(data,path):
	with open(path,'w',encoding='UTF-8') as file:
		yaml.dump(data, file, allow_unicode=True, sort_keys=False)

def load(path):
	with open(path,'r',encoding='UTF-8') as file:
		return yaml.safe_load(file)