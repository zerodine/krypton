__author__ = 'thospy'
'''
    The machine readable index format is a list of records that can be
   easily parsed by a machine.  The document is 7-bit clean, and as such
   is sent with no encoding and Content-Type: text/plain.

   The machine readable response begins with an optional information
   line:

   info:<version>:<count>

      <version> = this is the version of this output format.
                  Currently, this is the number 1.

      <count> = the number of keys returned in this response.  Note
                this is the number of keys, and not the number of
                lines returned.  That is, it should match the number
                of "pub:" lines returned.

   If this optional line is not included, or the version information is
   not supplied, the version number is assumed to be 1.

   The key listings themselves are made up of several lines per key.
   The first line specifies the primary key:

   pub:<keyid>:<algo>:<keylen>:<creationdate>:<expirationdate>:<flags>

      <keyid> = this is either the fingerprint or the key ID of the
                key.  Either the 16-digit or 8-digit key IDs are
                acceptable, but obviously the fingerprint is best.  A
                keyserver should use the most specific of the key IDs
                that it has available.  Since it is not possible to
                calculate the key ID from a V3 key fingerprint, for V3
                keys this should be either the 16-digit or 8-digit
                key ID only.

      <algo> = the algorithm number from [4].  (i.e. 1==RSA, 17==DSA,
               etc).

      <keylen> = the key length (i.e. 1024, 2048, 4096, etc.)

      <creationdate> = creation date of the key in standard RFC-2440
                       [4] form (i.e. number of seconds since 1/1/1970
                       UTC time)

      <expirationdate> = expiration date of the key in standard
                         RFC-2440 [4] form (i.e. number of seconds
                         since 1/1/1970 UTC time)

      <flags> = letter codes to indicate details of the key, if any.
                Flags may be in any order.  The meaning of "disabled"
                is implementation-specific.  Note that individual
                flags may be unimplemented, so the absence of a given
                flag does not necessarily mean the absence of the
                detail.

          r == revoked
          d == disabled
          e == expired

   Following the "pub" line are one or more "uid" lines to indicate user
   IDs on the key:

   uid:<escaped uid string>:<creationdate>:<expirationdate>:<flags>

      <escaped uid string> = the user ID string, with HTTP %-escaping
                             for anything that isn't 7-bit safe as
                             well as for the ":" character.  Any other
                             characters may be escaped, as desired.

   creationdate, expirationdate, and flags mean the same here as in the
   "pub" line.  The information is taken from the self-signature, if
   any, and applies to the user ID in question, and not to the key as a
   whole.

   Note that empty fields are allowed.  For example, a key with no
   expiration date would have the <expirationdate> field empty.  Also,
   a keyserver that does not track a particular piece of information
   may leave that field empty as well.  Colons for empty fields on the
   end of each line may be left off, if desired.
'''

import logging


class MrParser(object):
    """

    """

    version = 1
    logger = logging.getLogger("krypton")

    _raw = []

    def __init__(self, jsonData):
        """

        :param jsonData:
        """
        self._raw = jsonData

    def parse(self):
        """


        :return:
        """
        data = [self._start()]
        for key in self._raw:
            x = self._listKey(key)
            if x:
                data.append(x)

            x = self._listUid(key)
            if x:
                data.append(x)

            x = self._listUat(key)
            if x:
                data.append(x)

        return "\n".join(data)

    def _start(self):
        """
        info:<version>:<count>
        """
        return "info:%i:%i" % (self.version, len(self._raw))

    def _listKey(self, key):
        """
        pub:<keyid>:<algo>:<keylen>:<creationdate>:<expirationdate>:<flags>

        :param key:
        """
        return "pub:%(keyid)s:%(algo)s:%(keylen)s:%(creationdate)s:%(expirationdate)s:%(flags)s" % ({
            "keyid": key["key_id"],
            "algo": key["raw_pub_algorithm"],
            "keylen": key["key_lenght"],
            "creationdate": key["raw_creation_time"],
            "expirationdate": key["expiration_time"],
            "flags": ""
        })

    def _listUat(self, key):
        """
        uat::::
        """
        if not "UserAttributePacket" in key:
            return ""

        data = []
        for idVal in key["UserAttributePacket"]:
            data.append("uat::::")
        return "\n".join(data)

    def _listUid(self, key):
        """
        uid:<escaped uid string>:<creationdate>:<expirationdate>:<flags>

        :param key:
        """
        data = []
        for id in key["UserIDPacket"]:
            data.append("uid:%(uidstring)s:%(creationdate)s:%(expirationdate)s:%(flags)s" % (
                {
                "uidstring": id["user"],
                "creationdate": "",
                "expirationdate": "",
                "flags": ""
                })
            )
        return "\n".join(data)