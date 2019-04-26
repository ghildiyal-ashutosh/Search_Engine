import sys
import os

class FileHandling:

    """
    Read the files as lines
    """
    def read_file_lines(self, filename):
        obj  = open(filename, 'r')
        data = obj.readlines()
        lines = []
        for d in data:
            lines.append(d.strip())
        return lines

    """
    Read the file as a string
    """
    def read_file(self, filename):
        obj  = open(filename, 'r')
        return obj.read()
    
    def create_folder(self, folder):
        try:
            dir = os.path.dirname(folder)
            if dir != '' and not os.path.exists(dir):
                os.makedirs(dir)
        except:
            print('Create Folder:: Could not create all the folders')
            sys.exit()

    """
    Save the file with the content and filename passed
    Creates the directory if not present
    """
    def save_file(self, content, filename):
        try:
            dir = os.path.dirname(filename)
            if dir != '' and not os.path.exists(dir):
                os.makedirs(dir)
            f = open(filename, 'w+')
            f.write(content)
            f.close()
        except:
            print('Save File:: System Error! Looks like the file/folder was not found')
            sys.exit()

    """
    Get All files from the given folder
    """
    def get_all_files(self, folder = None):
        try:
            if folder is None:
                return []
            filenames  = []
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    if filename.startswith('.'):
                        continue
                    filenames.append(filename)

            return filenames
        except:
            print('Unable to get all the files of the folder..')
            sys.exit()