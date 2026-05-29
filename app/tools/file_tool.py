import os


class FileTool:

    def create_folder(self, path):
        os.makedirs(path, exist_ok=True)

    def write_file(self, path, content):

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)