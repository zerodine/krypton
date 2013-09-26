#import StringIO
import datetime
#from M2Crypto.BIO import BIO
import binascii

__author__ = 'thospy'

import json
import pgpdump
from pgpdump.utils import (PgpdumpException, get_int2, get_int4, get_mpi, get_key_id, get_int_bytes)
import base64
import hashlib
import math
import logging
import M2Crypto


class JsonParser(object):
    """

    This are the available signature types

            00: "Signature of a binary document",
            01: "Signature of a canonical text document",
            02: "Standalone signature",
            16: "Generic certification of a User ID and Public Key packet",     SIG
            17: "Persona certification of a User ID and Public Key packet",     SIG1
            18: "Casual certification of a User ID and Public Key packet",      SIG2
            19: "Positive certification of a User ID and Public Key packet",    SIG3
            24: "Subkey Binding Signature",
            25: "Primary Key Binding Signature",
            31: "Signature directly on a key",
            32: "Key revocation signature",
            40: "Subkey revocation signature",
            48: "Certification revocation signature",
            64: "Timestamp signature",
            80: "Third-Party Confirmation signature",
    """

    _raw = None
    _organized = {}
    _primaries = []
    logger = logging.getLogger("krypton")
    keyId = None
    otherKeys = []

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
        data["foreignKeys"] = list(set(self.otherKeys))

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
        if not sub:
            self.keyId = packet.key_id

        try:
            keyLength = int(math.log(packet.modulus, 2)) + 1
        except TypeError:
            keyLength = 0

        try:
            rsaPubKey = M2Crypto.RSA.new_pub_key(
                (
                    M2Crypto.m2.bn_to_mpi(M2Crypto.m2.hex_to_bn(binascii.hexlify(str(packet.exponent)))),
                    M2Crypto.m2.bn_to_mpi(M2Crypto.m2.hex_to_bn(binascii.hexlify(str(packet.modulus)))),
                )
            )
            #demodata = base64.b64encode(rsaPubKey.public_encrypt(data="This is a TEST", padding=1))
            xx = M2Crypto.BIO.MemoryBuffer()
            rsaPubKey.save_key_bio(xx, None)
            rsaKey = base64.b64encode(str(xx.getvalue()))

        except M2Crypto.RSA.RSAError, e:
            self.logger.warn("Could not reproduce RSA Public key for key with ID %s (%s)", (packet.key_id, str(e)))
            rsaKey = None

        data = {
            "key_id": str(packet.key_id).upper(),
            "key_id_32": str(packet.fingerprint[-8:]).upper(),
            "key_id_64": str(packet.fingerprint[-16:]).upper(),
            "fingerprint_v3": str(packet.fingerprint[-32:]).upper(),
            "fingerprint_v4": str(packet.fingerprint[-40:]).upper(),
            "fingerprint": str(packet.fingerprint).upper(),
            "pubkey_version": packet.pubkey_version,
            "raw_creation_time": packet.raw_creation_time,
            "creation_time": str(packet.creation_time),
            "raw_days_valid": packet.raw_days_valid,
            "expiration_time": packet.expiration_time,
            "pub_algorithm": packet.pub_algorithm,
            "pub_algorithm_type": packet.pub_algorithm_type,
            "raw_pub_algorithm": packet.raw_pub_algorithm,
            "rsa_public_key": rsaKey,
            #"demodata": demodata,
            #"prime": packet.prime, # may cause OverflowError exception cause "MongoDB can only handle up to 8-byte ints"
            #"group_order": packet.group_order, # may cause OverflowError exception cause "MongoDB can only handle up to 8-byte ints"
            #"group_gen": packet.group_gen, # may cause OverflowError exception cause "MongoDB can only handle up to 8-byte ints"
            #"key_value": packet.key_value, # may cause OverflowError exception cause "MongoDB can only handle up to 8-byte ints"
            "key_lenght": keyLength
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
            # Check for revocation
            isRevocation = False
            if int(s.raw_sig_type) in [32, 40, 48]:
                isRevocation = True

            # get siglevel
            index_sig_text = None
            if 16 <= s.raw_sig_type <= 19:
                type = str(s.raw_sig_type - 16)
                if type == "0":
                    type = ""
                index_sig_text = "sig%s" % type

            # get signer name
            if s.key_id in self.keyId:
                signer_name = "[selfsig]"
            else :
                self.otherKeys.append(s.key_id)
                signer_name = "Mr. %s" % s.key_id

            data.append(self._serialize({
                "sig_version": s.sig_version,
                "sig_type": s.sig_type,
                "sig_type_raw": s.raw_sig_type,
                "index_sig_text": index_sig_text,
                "pub_algorithm": s.pub_algorithm,
                "hash_algorithm": s.hash_algorithm,
                "raw_creation_time": s.raw_creation_time,
                "creation_time": s.creation_time,
                "raw_expiration_time": s.raw_expiration_time,
                "expiration_time": s.expiration_time,
                "key_id": s.key_id,
                "key_id_32": s.key_id[-8:],
                "key_id_64": s.key_id[-16:],
                "hash2": s.hash2,
                "isRevocation": isRevocation,
                "signer_name": signer_name#,
                #"signatureSubPackages": self.parseSignatureSubPacket(s.subpackets)
            }))
        return data

    def parseSignatureSubPacket(self, signatureSub):
        if not signatureSub:
            signatureSub = []

        data = []

        for s in signatureSub:
            x = vars(s)
            if s.subtype in [2, 9]:
                x["data_human"] = get_int4(s.data, 0)
            elif s.subtype == 3:
                x["data_human"] = get_int4(s.data, 0)
            elif s.subtype == 16:
                x["data_human"] = get_key_id(s.data, 0)
            x["name"] = s.name
            data.append(self._serialize(x))
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