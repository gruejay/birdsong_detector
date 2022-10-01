from http.client import CannotSendHeader
import xenocanto as xc 

meta = xc.metadata("Eastern Bluebird q:A".split())
print(meta)