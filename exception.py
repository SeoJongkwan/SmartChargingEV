class FileExistException(Exception):
    def __init__(self):
        super().__init__("파일이 없습니다.")