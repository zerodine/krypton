__author__ = 'thospy'

import json
import pgpdump

class JsonParser(object):
    _raw = None
    _organized = {
        "publickey": None,
        "packages":[],
    }

    def __init__(self, asciiData):
        self._raw = pgpdump.AsciiData(asciiData)
        self._organizeData()

    def dump(self, pretty=False):

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
        if pretty:
            return json.dumps(data, indent=4, sort_keys=True)

        return json.dumps(data)

    def parsePublicKeyPacket(self, packet):
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
            "modulus":              packet.modulus,
            "exponent":             packet.exponent,
            "prime":                packet.prime,
            "group_order":          packet.group_order,
            "group_gen":            packet.group_gen,
            "key_value":            packet.key_value,
        }
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
            #pprint(vars(s))
        return data

    def parseUserIDPacket(self, packet):
        data = {
            "user":         packet["packet"].user,
            "user_name":    packet["packet"].user_name,
            "user_email":   packet["packet"].user_email,
            "signatures":   self.parseSignaturePacket(packet["signatures"])
        }
        return self._serialize(data)

    def parseUserAttributePacket(self, packet):
        self.raw_image_format = None
        self.image_format = None
        self.image_data = None
        data = {
             "image_format":        packet["packet"].image_format,
             "image_data":          "" #packet["packet"].image_data,
        }
        return self._serialize(data)

    def parsePublicSubkeyPacket(self, packet):
        data = self.parsePublicKeyPacket(packet["packet"])
        data["signatures"] = self.parseSignaturePacket(packet["signatures"])
        return data

    def _serialize(self, data):
        for k, v in data.iteritems():
            t = str(v.__class__.__name__).lower()
            if t == "str":
                continue
            elif t == "int":
                data[k] = str(v)
            elif t == "bytearray":
                data[k] = "BYTES"
            elif t == "datetime":
                data[k] = str(v)

        return data

    def _organizeData(self):
        #x = {"base":None, "signatures":[]}
        x = None

        for packet in self._raw.packets():
            packet.parse()

            if isinstance(packet, pgpdump.packet.PublicSubkeyPacket):
                #print "PublicSubkeyPacket"
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet":packet, "signatures":[]}
                #pprint(vars(packet))

            elif isinstance(packet, pgpdump.packet.PublicKeyPacket):
                #print "PublicKeyPacket"
                #x = None
                self._organized['publickey'] = packet

            elif isinstance(packet, pgpdump.packet.UserIDPacket):
                #print "UserIDPacket"
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet":packet, "signatures":[]}
                #pprint(vars(packet))

            elif isinstance(packet, pgpdump.packet.SignaturePacket):
                #print "SignaturePacket"
                if x is not None:
                    x["signatures"].append(packet)

                #pprint(vars(packet))
                #for sp in packet.subpackets:
                    #pprint(vars(sp))
                    #pass

            elif isinstance(packet, pgpdump.packet.UserAttributePacket):
                #print "UserAttributePacket"
                if x is not None:
                    self._organized["packages"].append(x)
                x = {"packet":packet, "signatures":[]}
                #pprint(vars(packet))

            else:
                print "NOT KNOWN: %s" % packet

            #print packet.fingerprint
        if x is not None:
            self._organized["packages"].append(x)