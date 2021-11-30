# -*- coding:utf-8 -*-
"""
@Author: Mas0n
@File: typora.py
@Time: 2021-11-29 21:24
@Desc: It's all about getting better.
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from base64 import b64decode, b64encode
from jsbeautifier import beautify
from jsmin import jsmin
from os import listdir, urandom, makedirs
from os.path import isfile, isdir, join as pjoin, split as psplit
from loguru import logger as log
from masar import extract_asar, pack_asar
import argparse

key = [0x4B029A9482B3E14E, 0xF157FEB4B4522F80, 0xE25692105308F4BE, 0x6DD58DDDA3EC0DC2]
aesKey = b""
for akey in key:
    aesKey += int.to_bytes(akey, byteorder="little", length=8)


def _mkdir(_path):
    try:
        makedirs(_path)
    except FileExistsError:
        log.warning(f"May FolderExists: {_path}")


def decScript(b64: bytes, prettify: bool):
    lCode = b64decode(b64)
    # iv: the first 16 bytes of the file
    aesIv = lCode[0:16]
    # cipher text
    cipherText = lCode[16:]
    # AES 256 CBC
    ins = AES.new(key=aesKey, iv=aesIv, mode=AES.MODE_CBC)
    code = unpad(ins.decrypt(cipherText), 16, 'pkcs7')
    if prettify:
        code = beautify(code.decode()).encode()
    return code


def extractWdec(asarPath, path, prettify):
    """
    :param asarPath: asar out dir
    :param path: out dir
    :return: None
    """
    # try to create empty dir to save extract files
    path = pjoin(path, "tmp_app")
    _mkdir(path)
    log.info(f"extract asar file: {asarPath}")
    # extract app.asar to {path}/*
    extract_asar(asarPath, path)
    log.success(f"extract ended.")

    log.info(f"read Directory: {path}")
    # construct the save directory {pathRoot}/dec_app
    outPath = pjoin(psplit(path)[0], "dec_app")
    # try to create empty dir to save decryption files
    _mkdir(outPath)
    log.info(f"set Directory: {outPath}")
    # enumerate extract files
    fileArr = listdir(path)
    for name in fileArr:
        # read files content
        fpath = pjoin(path, name)
        scode = open(fpath, "rb").read()
        log.info(f"open file: {name}")
        # if file suffix is *.js then decryption file
        if isfile(fpath) and name.endswith(".js"):
            scode = decScript(scode, prettify)
        else:
            log.debug(f"skip file: {name}")
        # save content {outPath}/{name}
        open(pjoin(outPath, name), "wb").write(scode)
        log.success(f"decrypt and save file: {name}")


def encScript(_code: bytes, compress):
    if compress:
        _code = jsmin(_code.decode(), quote_chars="'\"`").encode()
    aesIv = urandom(16)
    cipherText = aesIv + _code
    ins = AES.new(key=aesKey, iv=aesIv, mode=AES.MODE_CBC)
    enc = ins.encrypt(pad(cipherText, 16, 'pkcs7'))
    lCode = b64encode(enc)
    return lCode


def packWenc(path, outPath, compress):
    """
    :param path: out dir
    :param outPath: pack path app.asar
    :param compress: Bool
    :return: None
    """
    if not isdir(outPath):
        log.error("plz input Directory for app.asar")
        raise NotADirectoryError
    encFilePath = pjoin(psplit(outPath)[0], "enc_app")
    _mkdir(encFilePath)

    outFilePath = pjoin(outPath, "app.asar")
    log.info(f"set outFilePath: {outFilePath}")
    fileArr = listdir(path)

    for name in fileArr:
        fpath = pjoin(path, name)
        if isdir(fpath):
            log.error("TODO: found folder")
            raise IsADirectoryError

        scode = open(fpath, "rb").read()
        log.info(f"open file: {name}")
        if isfile(fpath) and name.endswith(".js"):
            scode = encScript(scode, compress)

        open(pjoin(encFilePath, name), "wb").write(scode)
        log.success(f"encrypt and save file: {name}")

    log.info("ready to pack")
    pack_asar(encFilePath, outFilePath)
    log.success("pack done")


def main():
    argParser = argparse.ArgumentParser(
        description="[extract and decryption / pack and encryption] app.asar file from [Typora].",
        epilog="If you have any questions, please contact [ MasonShi@88.com ]")
    argParser.add_argument("asarPath", type=str, help="app.asar file path/dir [input/ouput]")
    argParser.add_argument("dirPath", type=str, help="as tmp and out directory.")

    argParser.add_argument('-u', dest='mode', action='store_const',
                           const=packWenc, default=extractWdec,
                           help='pack & encryption (default: extract & decryption)')
    argParser.add_argument('-f', dest='format', action='store_const',
                           const=True, default=False,
                           help='enabled prettify/compress (default: disabled)')
    args = argParser.parse_args()

    args.mode(args.asarPath, args.dirPath, args.format)
    log.success("Done!")


if __name__ == '__main__':
    main()
