# pip install pycryptodome == 3.9.9

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import os
import base64

code = '2ikacwtwph'

ENV_PROFILE = os.getenv("ENV")
if ENV_PROFILE == "pro":
    from NetOpsAssets import prd_settings as config
elif ENV_PROFILE == "test":
    from NetOpsAssets import test_settings as config
else:
    from NetOpsAssets import settings as config


# 创建秘钥对
def CreateRSAKeys():
    key = RSA.generate(2048)
    encrypted_key = key.exportKey(passphrase=code, pkcs=8, protection="scryptAndAES128-CBC")
    # 私钥
    with open('../keys/my_private_rsa_key.bin', 'wb') as f:
        f.write(encrypted_key)
    # 公钥
    with open('../keys/my_rsa_public.pem', 'wb') as f:
        f.write(key.publickey().exportKey())


# 加密
def Encrypt(filename):
    data = ''
    with open(filename, 'rb') as f:
        data = f.read()
    with open(filename, 'wb') as out_file:
        # 收件人秘钥 - 公钥
        recipient_key = RSA.import_key(open(config.PUBLIC_KEY_PATH).read())
        session_key = get_random_bytes(16)
        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        out_file.write(cipher_rsa.encrypt(session_key))
        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        out_file.write(cipher_aes.nonce)
        out_file.write(tag)
        out_file.write(ciphertext)


# 解密
def Descrypt(filename):
    with open(filename, 'rb') as fobj:
        private_key = RSA.import_key(open(config.PRIVATE_KEY_PATH).read(), passphrase=code)
        enc_session_key, nonce, tag, ciphertext = [fobj.read(x)
                                                   for x in (private_key.size_in_bytes(),
                                                             16, 16, -1)]
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    with open(filename, 'wb') as wobj:
        wobj.write(data)


# 文件重命名
def RenameFile(dir, filename):
    filename_bytes = filename.encode('utf-8')
    filename_bytes_base64 = base64.encodebytes(filename_bytes)

    filename_bytes_base64 = filename_bytes_base64[::-1][1:]
    new_filename = filename_bytes_base64.decode('utf-8') + '.crypt1'
    print(os.path.join(dir, filename))
    print(os.path.join(dir, new_filename))
    os.rename(os.path.join(dir, filename), os.path.join(dir, new_filename))
    return new_filename


# 解密并且恢复名字
def ReserveFilename(dir, filename):
    f = filename
    filename = filename[::-1][7:][::-1]
    filename_base64 = filename[::-1] + '\n'
    filename_bytes_base64 = filename_base64.encode('utf-8')
    ori_filename = base64.decodebytes(filename_bytes_base64).decode('utf-8')
    print(os.path.join(dir, f))
    print(os.path.join(dir, ori_filename))
    os.rename(os.path.join(dir, f), os.path.join(dir, ori_filename))
    return ori_filename


# 文件夹所有文件加密
def encryptFolder(rootDir):
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            filename = os.path.join(root, f)
            Encrypt(filename)
            RenameFile(root, f)


# 文件夹所有文件解密
def descryptFolder(rootDir):
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            filename = os.path.join(root, f)
            Descrypt(filename)
            ReserveFilename(root, f)


# 加密单个文件
def SingleFileEncrypt(rootDir, filename):
    Encrypt(filename)
    new_filename = RenameFile(rootDir, os.path.basename(filename))
    print("new_filename========>", new_filename)
    return new_filename


# 解密单个文件
def SingleFileDescrypt(rootDir, filename):
    Descrypt(filename)
    ori_filename = ReserveFilename(rootDir, os.path.basename(filename))
    return ori_filename


# option+command+c
# /Users/congxingwang/pythoncode/weboffice/keys/my_private_rsa_key.bin

if __name__ == '__main__':

    rootDir = "/Users/congxingwang/Desktop/safeFile/"
    '''
    1.第一步执行创建秘钥函数
    CreateRSAKeys()
    2.第二步加密文件所有文件
    encryptFolder(rootDir)
    3.解密文件前,先注释第二部代码
    #CreateRSAKeys()
    #encryptFolder(rootDir)
    descryptFolder(rootDir)
    '''
    # CreateRSAKeys()
    #encryptFolder(rootDir)
    #descryptFolder(rootDir)
