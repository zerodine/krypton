import gnupg
import os

__author__ = 'thospy'

import unittest


class MyTestCase(unittest.TestCase):
    gpg = None
    basefolder = "demodata/mass"
    numKeys = 1000

    def setUp(self):
        self.gpg = gnupg.GPG(gnupghome='/tmp', gpgbinary="/usr/local/bin/gpg")

    def test_createbulkkeys(self):
        for i in range(self.numKeys):
            input_data = self.gpg.gen_key_input(key_type="RSA", key_length=1024*4)
            keyId = self.gpg.gen_key(input_data)
            print "No %s Created key with Id %s" % (i, keyId)
            folder = "%s/%s" % (self.basefolder, str(keyId)[0])
            file = "%s/%s.gpg" % (folder, keyId)
            self._mkdir(folder)
            ascii_armored_public_keys = self.gpg.export_keys(keyId)

            try:
                f = open(file, "w")
                f.write(ascii_armored_public_keys)
                f.close()
            except:
                raise

    def _mkdir(self, dir):
        if not os.path.isfile(dir) and not os.path.isdir(dir):
            os.mkdir(dir)

if __name__ == '__main__':
    unittest.main()
