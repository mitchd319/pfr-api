import json
import os
import logging
import fileutilities

class JSONSerializer:
    def __init__(self):
        pass

    '''
    Save a dictionary to a JSON format. Default indent to 4 for pretty print
    '''
    def save_dict_to_json(self, obj, file_name, indent=4, write_mode='w', overwrite=False):
        
        if os.path.exists(file_name):
            if overwrite:
                os.remove(os.path.abspath(file_name))
                logging.debug(f'Deleted existing file {os.path.abspath(file_name)}.')
            else:
                logging.debug(f'Did not delete file {os.path.abspath(file_name)} because it already exists.')
                return

        # If the directory does not exist, then create it
        if not fileutilities.Check_If_Directory_Exists(file_name):
            fileutilities.Create_Directory(file_name)

        # Create a new JSON object from a Python dictionary, specifying an indent for pretty print by default
        json_object = json.dumps(obj, default = lambda o:o.__dict__, indent=indent)
        # Write the JSON object to a file
        with open(file_name, write_mode) as outfile:
            outfile.write(json_object)
            logging.debug(f'Successfully cached {os.path.abspath(file_name)}.')

    def load_dict_from_json(self, file_name):
        with open(file_name, 'r') as openfile:
            json_object = json.load(openfile)
        return json_object