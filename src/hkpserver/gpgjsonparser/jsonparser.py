__author__ = 'thospy'

import json
import pgpdump
import base64
import hashlib
import math


class JsonParser(object):
    _raw = None
    _organized = {}
    _primaries = []

    def __init__(self, asciiData):
        self.reset()
        self._raw = pgpdump.AsciiData(asciiData)
        self._organizeData()

    def reset(self):
        self._raw = None
        self._organized = {
            "publickey": None,
            "packages":[],
        }
        self._primaries = []

    def dump(self, pretty=False, raw=False):
        data = self.parsePublicKeyPacket(self._organized['publickey'])

        for p in self._organized["packages"]:
            className = p["packet"].__class__.__name__
            method = getattr(self, 'parse' + className, None)
            if not method:
                print "method %s does not exist" % className
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
        data = {
            "key_id":               packet.key_id,
            "fingerprint":          packet.fingerprint,
            "pubkey_version":       packet.pubkey_version,
            "raw_creation_time":    packet.raw_creation_time,
            "creation_time":        str(packet.creation_time),
            "raw_days_valid":       packet.raw_days_valid,
            "expiration_time":      packet.expiration_time,
            "pub_algorithm":        packet.pub_algorithm,
            "pub_algorithm_type":   packet.pub_algorithm_type,
            "raw_pub_algorithm":    packet.raw_pub_algorithm,
            "modulus":              "LONGINT:%s" % packet.modulus,
            "exponent":             packet.exponent,
            "prime":                packet.prime,
            "group_order":          packet.group_order,
            "group_gen":            packet.group_gen,
            "key_value":            packet.key_value,
            "key_lenght":           int(math.log(packet.modulus, 2)) + 1
        }

        # adding primary references
        if not sub:
            for key, val in  self._primaries.iteritems():
                data["primary_%s" % key] = val

        return self._serialize(data)

    def parseSignaturePacket(self, signatures = [] ):
        data = []
        for s in signatures:
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
                "hash2": s.hash2
            }))
        return data

    def parseUserIDPacket(self, packet):
        primary = False
        if packet["packet"].user == self._primaries["UserIDPacket"]:
            primary = True

        data = {
            "user":         packet["packet"].user,
            "user_name":    packet["packet"].user_name,
            "user_email":   packet["packet"].user_email,
            "primary":      primary,
            "signatures":   self.parseSignaturePacket(packet["signatures"])
        }
        #print packet["packet"].user
        return self._serialize(data)

    def parseUserAttributePacket(self, packet):
        h = hashlib.new('sha1')
        h.update(packet["packet"].image_data)
        hashval = h.hexdigest()

        primary = False
        if hashval == self._primaries["UserAttributePacket"]:
            primary = True

        data = {
             "image_format":        packet["packet"].image_format,
             "image_data":          packet["packet"].image_data,
             "hash":                hashval,
             "primary":             primary,
             "hash_algorithm":      "sha1"
        }
        return self._serialize(data)

    def parsePublicSubkeyPacket(self, packet):
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
                x = {"packet":packet, "signatures":[]}

            elif isinstance(packet, pgpdump.packet.PublicKeyPacket):
                self._organized['publickey'] = packet

            elif isinstance(packet, pgpdump.packet.UserIDPacket):
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet":packet, "signatures":[]}
                self._primaries["UserIDPacket"] = packet.user
                #pprint(vars(packet))

            elif isinstance(packet, pgpdump.packet.SignaturePacket):
                if x is not None:
                    x["signatures"].append(packet)

                #pprint(vars(packet))
                #for sp in packet.subpackets:
                    #pprint(vars(sp))
                    #pass

            elif isinstance(packet, pgpdump.packet.UserAttributePacket):
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet":packet, "signatures":[]}

                h = hashlib.new('sha1')
                h.update(packet.image_data)
                self._primaries["UserAttributePacket"] = h.hexdigest()


            else:
                print "NOT KNOWN: %s" % packet

            #print packet.fingerprint
        if x is not None:
            self._organized["packages"].append(x)

        print self._primaries