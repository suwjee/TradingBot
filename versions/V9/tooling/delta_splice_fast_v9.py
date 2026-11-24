"""Exact byte splice transport using C-backed prefix/suffix comparisons.
Candidate transport only until equivalence with all legacy delta records is verified.
"""
import base64, hashlib

def b64(value): return base64.b64encode(value).decode("ascii")
def sha(value): return hashlib.sha256(value).hexdigest()

def common_prefix(a,b):
    lo,hi=0,min(len(a),len(b))
    while lo<hi:
        mid=(lo+hi+1)//2
        if a[:mid]==b[:mid]:lo=mid
        else:hi=mid-1
    return lo

def common_suffix(a,b,limit):
    lo,hi=0,limit
    while lo<hi:
        mid=(lo+hi+1)//2
        if a[len(a)-mid:]==b[len(b)-mid:]:lo=mid
        else:hi=mid-1
    return lo

def make_delta_fast(before,after):
    if type(before) is not bytes or type(after) is not bytes:raise TypeError('exact bytes required')
    if before==after:
        p,s=len(before),0;h=sha(before)
        return {'prefix':p,'suffix':s,'old':'','new':'','before_sha256':h,'after_sha256':h,'before_bytes':len(before),'after_bytes':len(after)}
    p=common_prefix(before,after);s=common_suffix(before,after,min(len(before),len(after))-p)
    return {'prefix':p,'suffix':s,'old':b64(before[p:len(before)-s]),'new':b64(after[p:len(after)-s]),'before_sha256':sha(before),'after_sha256':sha(after),'before_bytes':len(before),'after_bytes':len(after)}
