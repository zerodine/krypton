__author__ = 'thospy'

import tornado.template

from basecontroller import BaseController
from krypton.hkpserver.libs.gpgjsonparser import MrParser


# TODO: add X-HKP-Results-Count: 8 header to requests
class LookupController(BaseController):
    """

    """

    options = []
    machineReadable = False
    noModification = False
    fingerprint = False
    hash = False
    exact = False

    searchHex = False
    searchString = None

    @staticmethod
    def routes(prefix="", applicationContext=None):
        """

        :param prefix:
        :param applicationContext:
        :return:
        """
        return r"%s/lookup(.*)" % prefix, LookupController, dict(applicationContext=applicationContext)

    def get(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        # Parsing Options
        self.options = str(self.get_argument("options", default=None, strip=False)).lower().split(",")
        self._parseOptions()

        # Parsing Fingerprint and Exact
        self._parseOtherOptions(
            fingerprint=self.get_argument("fingerprint", default="off", strip=False),
            exact=self.get_argument("exact", default="off", strip=False),
            hash=self.get_argument("hash", default="off", strip=False))

        # Parsing Search
        searchData = self._parseSearch(self.get_argument("search", default="", strip=False))
        self.searchHex = searchData["searchHex"]
        self.searchString = searchData["searchString"]

        # Parsing Operation and run it
        op = self.get_argument("op", default="index", strip=False)
        getattr(self, "op_%s" % str(op).lower())(**kwargs)

    # noinspection PyShadowingBuiltins
    def _parseOtherOptions(self, fingerprint, exact, hash):
        """

        :param fingerprint:
        :param exact:
        """
        on = "on"
        if on in str(fingerprint).lower():
            self.fingerprint = True
        if on in str(exact).lower():
            self.exact = True
        if on in str(hash).lower():
            self.hash = True

    def _parseOptions(self):
        """
        Parses given options in &options=x,y...

        """
        if "mr" in self.options:
            self.machineReadable = True
        if "nm" in self.options:
            self.noModification = True

    def op_index(self, verbose=False):
        """

        :param verbose:
        :return:
        """
        data = self._getData()
        if self.machineReadable:
            self.set_header("Content-Type", "text/plain")
            mr = MrParser(data)
            self.write(mr.parse())
            return

        loader = tornado.template.Loader(self.buildPath("hkpserver/views"))

        template = "gpgindex.template.html"
        if verbose:
            template = "gpgvindex.template.html"
            # Get ID's of foreign keys
            for dat in data:
                if "foreignKeys" in dat:
                    dat["foreignKeys_names"] = {}
                    for x in dat["foreignKeys"]:
                        dat["foreignKeys_names"][x] = self.gpgModel.getKeyPrimaryUid(x)
                    dat["foreignKeys_names"][dat["key_id"]] = "[selfsig]"

        self.write(loader.load(template).generate(
            current="Lookup",
            gpgkeys=data,
            showFingerprint=self.fingerprint,
            showHash=self.hash,
            searchString=self.searchString))

    def op_vindex(self):
        """


        :return:
        """
        if self.machineReadable:
            self.op_index()
            return

        self.op_index(verbose=True)
        return

    def _getData(self):
        """


        :return:
        """
        self.gpgModel.connect(db=self.config.mongoDatabase)

        if self.searchHex:
            return self.gpgModel.searchKeyId(keyId=self.searchString, exact=self.exact)
        return self.gpgModel.searchKey(searchString=self.searchString, exact=self.exact)

    def op_get(self):
        """


        :return:
        """
        key = None
        self.gpgModel.connect(db=self.config.mongoDatabase)
        if self.searchHex:
            key = self.gpgModel.retrieveKey(keyId=self.searchString)

        if self.machineReadable:
            self.set_header("Content-Type", "application/pgp-keys")
            self.write(key)
            return
        loader = tornado.template.Loader(self.buildPath("hkpserver/views"))
        self.write(loader.load("gpgkey.template.html").generate(
            current="Get",
            fingerprint=self.searchString.upper(),
            key=key
        ))

    def op_hget(self):
        """


        :return:
        """

        self.gpgModel.connect(db=self.config.mongoDatabase)
        key = self.gpgModel.retrieveKey(hash=self.searchString)

        if self.machineReadable:
            self.set_header("Content-Type", "application/pgp-keys")
            self.write(key)
            return
        loader = tornado.template.Loader(self.buildPath("hkpserver/views"))
        self.write(loader.load("gpgkey.template.html").generate(
            current="Get Hash",
            fingerprint=self.searchString.upper(),
            key=key
        ))

    def op_stats(self):
        self.gpgModel.connect(db=self.config.mongoDatabase)

        statsDaily = self.gpgModel.getStatistics(onlyDay=True)
        statsHourly = self.gpgModel.getStatistics(onlyDay=False)
        numKeys = self.gpgModel.numberOfKeys()

        loader = tornado.template.Loader(self.buildPath("hkpserver/views"))
        self.write(loader.load("stats.template.html").generate(
            current="Statistics",
            applicationContext=self.applicationContext,
            statsDaily=statsDaily,
            statsHourly=statsHourly,
            numKeys=numKeys
        ))