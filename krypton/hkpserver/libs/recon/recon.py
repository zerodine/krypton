__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__version__ = "0.0.1"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "development"

import logging


class Recon(object):

    logger = logging.getLogger("krypton.recon")

    def syncPartners(self, reconPartner1, reconPartner2):
        stats = {"1": {"updated": 0, "missing": 0},"2": {"updated": 0, "missing": 0}, "changesTotal": 0}
        doneKeys = []
        hashPartner1 = reconPartner1.hashes()
        hashPartner2 = reconPartner2.hashes()

        if hashPartner1 is None or hashPartner2 is None:
            return None

        for x in hashPartner1.symmetric_difference(hashPartner2):
            keyHash, keyId = str(x).split(".")
            if keyId in doneKeys:
                self.logger.info("Already reconciled key %s" % keyId)
                continue

            keyPartner1 = reconPartner1.getKey(keyId=keyId)
            keyPartner2 = reconPartner2.getKey(keyId=keyId)

            if not keyPartner1 and keyPartner2:
                self.logger.info("Reconcil %s from Partner2 to Partner1" % keyHash)
                if reconPartner1.storeKey(asciiArmoredKey=keyPartner2):
                    stats["1"]["missing"] += 1
            elif not keyPartner2 and keyPartner1:
                self.logger.info("Reconcil %s from Partner1 to Partner2" % keyHash)
                if reconPartner2.storeKey(asciiArmoredKey=keyPartner1):
                    stats["2"]["missing"] += 1
            elif len(keyPartner2) > len(keyPartner1):
                self.logger.info("Reconcil %s update from Partner2 to Partner1" % keyHash)
                if reconPartner1.storeKey(asciiArmoredKey=keyPartner2):
                    stats["1"]["updated"] += 1
            elif len(keyPartner1) > len(keyPartner2):
                self.logger.info("Reconcil %s update from Partner1 to Partner2" % keyHash)
                if reconPartner2.storeKey(asciiArmoredKey=keyPartner1):
                    stats["2"]["updated"] += 1
            else:
                self.logger.warning("!!Reconcil for %s not possible due to wrong hash or whatever" % keyHash)
            doneKeys.append(keyId)

        stats["changesTotal"] = stats["1"]["updated"] + stats["1"]["missing"] + stats["2"]["updated"] + stats["2"]["missing"]
        return stats
