__author__ = 'thospy'

import json
import pgpdump
import base64
import hashlib
import math
import logging


class JsonParser(object):
    """

    sig_types = {
        00: "Signature of a binary document",
        01: "Signature of a canonical text document",
        02: "Standalone signature",
        16: "Generic certification of a User ID and Public Key packet",
        17: "Persona certification of a User ID and Public Key packet",
        18: "Casual certification of a User ID and Public Key packet",
        19: "Positive certification of a User ID and Public Key packet",
        24: "Subkey Binding Signature",
        25: "Primary Key Binding Signature",
        31: "Signature directly on a key",
        32: "Key revocation signature",
        40: "Subkey revocation signature",
        48: "Certification revocation signature",
        64: "Timestamp signature",
        80: "Third-Party Confirmation signature",
    }
    """

    _raw = None
    _organized = {}
    _primaries = []
    logger = logging.getLogger("krypton")

    def __init__(self, asciiData):
        """

        :param asciiData:
        """
        self.reset()
        self._raw = pgpdump.AsciiData(asciiData)
        self._organizeData()

    def reset(self):
        """


        """
        self._raw = None
        self._organized = {
            "publickey": None,
            "packages": [],
        }
        self._primaries = []

    def dump(self, pretty=False, raw=False):
        """

        :param pretty:
        :param raw:
        :return:
        """
        data = self.parsePublicKeyPacket(self._organized['publickey'])

        for p in self._organized["packages"]:
            className = p["packet"].__class__.__name__
            method = getattr(self, 'parse' + className, None)
            if not method:
                self.logger.critical("Cannot parse Packet with name %s because parser with the name %s"
                                     "Does not exists! That's not good!" % (className, 'parse' + className))
                continue
            else:
                if not className in data:
                    data[className] = []

                data[className].append(method(p))

        self._primaries = []

        if pretty:
            return json.dumps(data, indent=4, sort_keys=False)
        if raw:
            return json.loads(json.dumps(data, sort_keys=False))
        return json.dumps(data, sort_keys=False)

    def parsePublicKeyPacket(self, packet, sub=False):
        """

        :param packet:
        :param sub:
        :return:
        """
        data = {
            "key_id": packet.key_id,
            "key_id_32": packet.fingerprint[-8:],
            "key_id_64": packet.fingerprint[-16:],
            "fingerprint_v3": packet.fingerprint[-32:],
            "fingerprint_v4": packet.fingerprint[-40:],
            "fingerprint": packet.fingerprint,
            "pubkey_version": packet.pubkey_version,
            "raw_creation_time": packet.raw_creation_time,
            "creation_time": str(packet.creation_time),
            "raw_days_valid": packet.raw_days_valid,
            "expiration_time": packet.expiration_time,
            "pub_algorithm": packet.pub_algorithm,
            "pub_algorithm_type": packet.pub_algorithm_type,
            "raw_pub_algorithm": packet.raw_pub_algorithm,
            "modulus": "LONGINT:%s" % packet.modulus,
            "exponent": packet.exponent,
            "prime": packet.prime,
            "group_order": packet.group_order,
            "group_gen": packet.group_gen,
            "key_value": packet.key_value,

            #TODO: check for "TypeError: a float is required"
            "key_lenght": int(math.log(packet.modulus, 2)) + 1
        }

        # adding primary references
        if not sub:
            for key, val in self._primaries.iteritems():
                data["primary_%s" % key] = val

        return self._serialize(data)

    def parseSignaturePacket(self, signatures=None):
        """

        :param signatures:
        :return:
        """
        if not signatures:
            signatures = []
        data = []
        for s in signatures:
            isRevocation = False
            if int(s.raw_sig_type) in [32, 40, 48]:
                isRevocation = True

            data.append(self._serialize({
                "sig_version": s.sig_version,
                "sig_type": s.sig_type,
                "sig_type_raw": s.raw_sig_type,
                "pub_algorithm": s.pub_algorithm,
                "hash_algorithm": s.hash_algorithm,
                "raw_creation_time": s.raw_creation_time,
                "creation_time": s.creation_time,
                "raw_expiration_time": s.raw_expiration_time,
                "expiration_time": s.expiration_time,
                "key_id": s.key_id,
                "hash2": s.hash2,
                "isRevocation": isRevocation
            }))
        return data

    def parseUserIDPacket(self, packet):
        """

        :param packet: 
        :return: 
        """
        primary = False
        if packet["packet"].user == self._primaries["UserIDPacket"]:
            primary = True

        data = {
            "user": packet["packet"].user,
            "user_name": packet["packet"].user_name,
            "user_email": packet["packet"].user_email,
            "primary": primary,
            "signatures": self.parseSignaturePacket(packet["signatures"])
        }
        return self._serialize(data)

    def parseUserAttributePacket(self, packet):
        """

        :param packet: 
        :return: 
        """
        h = hashlib.new('sha1')
        h.update(packet["packet"].image_data)
        hashval = h.hexdigest()

        primary = False
        if hashval == self._primaries["UserAttributePacket"]:
            primary = True

        data = {
            "image_format": packet["packet"].image_format,
            "image_data": packet["packet"].image_data,
            "hash": hashval,
            "primary": primary,
            "hash_algorithm": "sha1"
        }
        return self._serialize(data)

    def parsePublicSubkeyPacket(self, packet):
        """


        :rtype : dict
        :param packet:
        :return: 
        """
        data = self.parsePublicKeyPacket(packet["packet"], sub=True)
        data["signatures"] = self.parseSignaturePacket(packet["signatures"])
        return data

    def _serialize(self, data):
        for k, v in data.iteritems():
            t = str(v.__class__.__name__).lower()
            if not v:
                data[k] = ""
            elif t == "str":
                continue
            elif t == "int":
                data[k] = str(v)
            elif t == "bytearray":
                data[k] = base64.b64encode(v)
            elif t == "datetime":
                data[k] = str(v)

        return data

    def _organizeData(self):
        """


        """
        x = None
        self._primaries = {
            "UserIDPacket": "",
            "UserAttributePacket": ""
        }
        for packet in self._raw.packets():
            packet.parse()

            if isinstance(packet, pgpdump.packet.PublicSubkeyPacket):
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet": packet, "signatures": []}

            elif isinstance(packet, pgpdump.packet.PublicKeyPacket):
                self._organized['publickey'] = packet

            elif isinstance(packet, pgpdump.packet.UserIDPacket):
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet": packet, "signatures": []}
                self._primaries["UserIDPacket"] = packet.user
            elif isinstance(packet, pgpdump.packet.SignaturePacket):
                if x is not None:
                    x["signatures"].append(packet)
            elif isinstance(packet, pgpdump.packet.UserAttributePacket):
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet": packet, "signatures": []}

                h = hashlib.new('sha1')
                h.update(packet.image_data)
                self._primaries["UserAttributePacket"] = h.hexdigest()
            else:
                self.logger.warning("Found an unknown packet while parsing key (%s)." % packet)

        if x is not None:
            self._organized["packages"].append(x)