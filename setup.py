from distutils.core import setup

setup(
    name='Krypton',
    version='0.1',
    packages=['src', 'src.hkpserver', 'src.hkpserver.libs', 'src.hkpserver.libs.gossip', 'src.hkpserver.libs.gpgmongo',
              'src.hkpserver.libs.gpgjsonparser', 'src.hkpserver.controllers'],
    url='https://github.com/zerodine/krypton',
    license='MIT',
    author='tspycher',
    author_email='me@tspycher.com',
    description='GPG/PGP Keyserver with many enhancements',
    install_requires=["PIL", "qrcode", "six", "tornado", "pymongo", "pgpdump", "M2Crypto"]
)
