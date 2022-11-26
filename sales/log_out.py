import logging
import os


def setup_logging(dir):
    #dir = "../_log"
    #dir = "C:/Users/rikiya/Desktop/売上管理/_log"
    formatter = "%(asctime)s : %(levelname)s : %(message)s"

    # ディレクトリの存在確認(なければ作成)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    file = os.path.join(dir, "py_scripts.log")
    logging.basicConfig(format=formatter, level=logging.INFO, filename=file)

    return logging