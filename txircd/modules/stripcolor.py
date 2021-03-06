from txircd.modbase import Mode

class StripColor(Mode):
    def strip_colors(self, msg):
        while chr(3) in msg:
            color_pos = msg.index(chr(3))
            strip_length = 1
            color_f = 0
            color_b = 0
            comma = False
            for i in range(color_pos + 1, len(msg) if len(msg) < color_pos + 6 else color_pos + 6):
                if msg[i] == ",":
                    if comma or color_f == 0:
                        break
                    else:
                        comma = True
                elif msg[i].isdigit():
                    if color_b == 2 or (not comma and color_f == 2):
                        break
                    elif comma:
                        color_b += 1
                    else:
                        color_f += 1
                else:
                    break
                strip_length += 1
            msg = msg[:color_pos] + msg[color_pos + strip_length:]
        msg = msg.replace(chr(2), "").replace(chr(29), "").replace(chr(31), "").replace(chr(15), "").replace(chr(22), "") # bold, italic, underline, plain, reverse
        return msg
    
    def checkPermission(self, user, cmd, data):
        if cmd not in ["PRIVMSG", "NOTICE"]:
            return data
        if chr(2) in data["message"] or chr(3) in data["message"] or chr(15) in data["message"] or chr(22) in data["message"] or chr(29) in data["message"] or chr(31) in data["message"]:
            exempt_chanops = "S" in self.ircd.servconfig["channel_exempt_chanops"]
            okchans = []
            okchanmod = []
            stripchans = []
            stripchanmod = []
            for index, chan in enumerate(data["targetchan"]):
                if "S" in chan.mode and (not exempt_chanops or not user.hasAccess(chan, "o")):
                    stripchans.append(chan.name)
                    stripchanmod.append(data["chanmod"][index])
                else:
                    okchans.append(chan)
                    okchanmod.append(data["chanmod"][index])
            data["targetchan"] = okchans
            data["chanmod"] = okchanmod
            if stripchans:
                user.handleCommand(cmd, None, [",".join([stripchanmod[i] + stripchans[i] for i in range(len(stripchans))]), self.strip_colors(data["message"])])
        return data

class Spawner(object):
    def __init__(self, ircd):
        self.ircd = ircd
    
    def spawn(self):
        return {
            "modes": {
                "cnS": StripColor()
            },
            "common": True
        }
    
    def cleanup(self):
        self.ircd.removeMode("cnS")