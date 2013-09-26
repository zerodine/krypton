from distutils.core import setup
#from setuptools import setup

setup(
    name='Krypton',
    version='0.1.2',
    packages=['krypton', 'krypton.hkpserver', 'krypton.hkpserver.libs', 'krypton.hkpserver.libs.gossip', 'krypton.hkpserver.libs.gpgmongo',
              'krypton.hkpserver.libs.gpgjsonparser', 'krypton.hkpserver.controllers'],
    url='https://github.com/zerodine/krypton',
    license='MIT',
    author='tspycher',
    author_email='me@tspycher.com',
    description='GPG/PGP Keyserver with many enhancements',
    install_requires=["PIL", "qrcode", "six", "tornado", "pymongo", "pgpdump", "M2Crypto"]
    #package_data={'krypton.hkpserver': [
    #    'views/themes/*.html',
    #    'views/*.html',
    #    'wwwroot/css/*.css',
    #    'wwwroot/fonts/*',
    #    'wwwroot/img/*',
    #    'wwwroot/js/vendor/*.js',
    #    'wwwroot/js/*.js',
    #    'wwwroot/*']}
    #data_files = [('krypton.hkpserver', ['negar/data/untouchable.dat'])],
)
