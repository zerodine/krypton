__author__ = 'thospy'

import tornado.web


class LookupController(tornado.web.RequestHandler):

    options = []
    machineReadable = False
    noModification = False
    fingerprint = False
    exact = False

    searchHex = False
    searchString = None

    @staticmethod
    def routes(prefix = ""):
        return r"%s/lookup(.*)" % prefix, eval("LookupController")

    def get(self, *args, **kwargs):
        # Parsing Options
        self.options = str(self.get_argument("options", default=None, strip=False)).lower().split(",")
        self._parseOptions()

        # Parsing Fingerprint and Exact
        self._parseOtherOptions(
            fingerprint=self.get_argument("fingerprint", default="off", strip=False),
            exact=self.get_argument("exact", default="off", strip=False))

        # Parsing Search
        self._parseSearch(self.get_argument("search", default="", strip=False))

        print self.searchString
        # Parsing Operation and run it
        op = self.get_argument("op", default="index", strip=False)
        getattr(self, "op_%s" % str(op).lower())(**kwargs)

    def _parseSearch(self, searchString):
        hex = "0x"
        s = str(searchString)
        if s.lower().startswith(hex):
            self.searchHex = True
            s = s[len(hex):]

        self.searchString = s

    def _parseOtherOptions(self, fingerprint, exact):
        on = "on"
        if on in str(fingerprint).lower():
            self.fingerprint = True
        if on in str(exact).lower():
            self.exact = True

    def _parseOptions(self):
        if "mr" in self.options:
            self.machineReadable = True
        if "nm" in self.options:
            self.noModification = True

    def op_index(self):
        self.write("Index")

    def op_vindex(self):
        self.write("Verbose Index")

    def op_get(self):
        self.write("Get")
        print self.searchString
        print self.searchHex