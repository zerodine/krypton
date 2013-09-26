from distutils.core import setup

setup(
    name='Krypton',
    version='0.1',
    packages=['krypton', 'krypton.hkpserver', 'krypton.hkpserver.libs', 'krypton.hkpserver.libs.gossip', 'krypton.hkpserver.libs.gpgmongo',
              'krypton.hkpserver.libs.gpgjsonparser', 'krypton.hkpserver.controllers'],
    url='https://github.com/zerodine/krypton',
    license='MIT',
    author='tspycher',
    author_email='me@tspycher.com',
    description='GPG/PGP Keyserver with many enhancements',
    install_requires=["PIL", "qrcode", "six", "tornado", "pymongo", "pgpdump", "M2Crypto"]
)
