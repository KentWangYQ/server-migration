import os
import config


def walk():
    """
    遍历源文件目录
    :return: Generator
    """
    for root in config.Source.include:
        for path, _, files in os.walk(root):
            if path not in config.Source.exclude:
                for file in files:
                    yield (path, file)
