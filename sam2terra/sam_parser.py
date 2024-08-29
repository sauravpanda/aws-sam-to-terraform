import yaml
class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None

SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)



def parse_sam_template(template_path):
    with open(template_path, 'r') as file:
        data = yaml.load(file, Loader=SafeLoaderIgnoreUnknown)
    return data