#!/usr/bin/env python3
"""Derive test-only bounded retention v5 observer from previously audited v4.

Only instrumentation, never engine source, is changed.
"""
from pathlib import Path
src=Path('/mnt/data/V9_final/tooling/semantic_trace_v4.py')
target=Path('/mnt/data/V9_final/tooling/semantic_trace_v5.py')
s=src.read_text()
s=s.replace("SCHEMA = 'tradingbot.v9.internal-observer.v4'", "SCHEMA = 'tradingbot.v9.internal-observer.v5'")
# Deliberately use streaming digest so large trace sidecars are never read whole.
insert="""\ndef stream_file_sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()
\n"""
s=s.replace("_CONTEXT_WRITER=None\n", "_CONTEXT_WRITER=None\n"+insert,1)
s=s.replace("hashlib.sha256(dest.read_bytes()).hexdigest()", "stream_file_sha256(dest)")
s=s.replace("hashlib.sha256(self.dest.read_bytes()).hexdigest()", "stream_file_sha256(self.dest)")
old="""        self.collection_refs={}
        self.collection_objects={}
        self.collection_files=[]
        self.force_fresh_collections=False
        self.mutable_generations=collections.Counter()"""
new="""        self.collection_refs={}
        # Bounded LRU: retain source identity only while a strong reference is
        # held. Eviction deletes id->ref, so Python id reuse can NEVER lead to
        # an incorrect recycled snapshot. A later encounter is serialized again.
        self.collection_objects=collections.OrderedDict()
        self.collection_weights={}
        self.collection_retained_estimate=0
        self.collection_retention_budget=384*1024*1024
        self.collection_max_objects=24
        self.collection_evictions=0
        self.collection_nonretained=0
        self.collection_files=[]
        self.force_fresh_collections=False"""
assert old in s
s=s.replace(old,new)
start=s.index('    def save_collection(self,source, fresh=False):')
end=s.index('    def save_chronology(self, chronology):',start)
replacement="""    def save_collection(self,source, fresh=False):
        key=id(source)
        sample=(next(iter(source.values())) if isinstance(source,dict) else source[0])
        is_mutable=type(sample).__name__!='Candle'
        if key in self.collection_refs:
            # Strict proof against id reuse: same object held strongly for every
            # active mapping, or there is no entry and we capture a fresh copy.
            if self.collection_objects.get(key) is not source:
                raise AssertionError('V5 collection identity unexpectedly changed')
            self.collection_objects.move_to_end(key)
            if not (fresh and is_mutable):
                return self.collection_refs[key]
        ordinal=len(self.collection_files)+1
        dest=Path(str(self.dest)+f'.collection.{ordinal:04d}.jsonl.gz')
        entries=source.items() if isinstance(source,dict) else enumerate(source)
        n=0;bytes_count=0;digest=hashlib.sha256()
        fp=dest.open('wb')
        try:
            with gzip.GzipFile(fileobj=fp,mode='wb',filename='',mtime=0,compresslevel=5) as z:
                for position,value in entries:
                    row={'source_ordinal':n,'source_key':stable_object(position,0,32,allow_namespace=True),
                         'source_value':stable_object(value,0,32,allow_namespace=True)}
                    payload=json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()+b'\\n'
                    digest.update(payload);z.write(payload);n+=1;bytes_count+=len(payload)
        finally:fp.close()
        element_type=type(sample).__name__
        immutable=(element_type=='Candle')
        summary={'file':dest.name,'entry_count':n,'container_kind':type(source).__name__,
                 'element_type':element_type,'source_candle_frozen':immutable,
                 'candidate_content_is_snapshot_at_first_use_only':not immutable and not fresh,
                 'fresh_boundary_snapshot':bool(fresh and is_mutable),
                 'jsonl_sha256':digest.hexdigest(),'gzip_sha256':stream_file_sha256(dest),
                 'uncompressed_bytes':bytes_count,
                 'snapshot_ordinal':ordinal}
        self.collection_files.append(summary)
        # Snapshot ordinal and memory-cache generation are implementation
        # details; semantic event references use content digests and lengths.
        stable_ref={k:v for k,v in summary.items() if k in
                   ('entry_count','container_kind','element_type','jsonl_sha256','source_candle_frozen',
                    'candidate_content_is_snapshot_at_first_use_only','fresh_boundary_snapshot')}
        if key in self.collection_objects:
            # Replace the snapshot for an explicitly refreshed mutable ledger.
            self.collection_refs[key]=stable_ref
            return stable_ref
        # This estimate is intentionally conservative. It limits strong
        # reference retention, NOT actual Engine memory or input history.
        weight=64+len(source)*(256 if immutable else 512)
        if weight>self.collection_retention_budget:
            self.collection_nonretained+=1
            # No memo entry is created, so later encounters cannot reuse an
            # out-of-date or id-colliding snapshot.
            return stable_ref
        while self.collection_objects and (
            len(self.collection_objects)>=self.collection_max_objects or
            self.collection_retained_estimate+weight>self.collection_retention_budget
        ):
            old_key,_=self.collection_objects.popitem(last=False)
            self.collection_refs.pop(old_key,None)
            self.collection_retained_estimate-=self.collection_weights.pop(old_key)
            self.collection_evictions+=1
        self.collection_objects[key]=source
        self.collection_refs[key]=stable_ref
        self.collection_weights[key]=weight
        self.collection_retained_estimate+=weight
        return stable_ref
"""
s=s[:start]+replacement+s[end:]
s=s.replace("'ordered_collection_sidecars':self.collection_files}","'ordered_collection_sidecars':self.collection_files,\n           'strong_collection_retention_estimate_bytes':self.collection_retained_estimate,\n           'strong_collection_retention_budget_bytes':self.collection_retention_budget,\n           'collection_lru_evictions':self.collection_evictions,\n           'collection_nonretained_snapshot_count':self.collection_nonretained}")
# Distinguish v5 clearly from v4 and require no proof of full semantics.
s=s.replace("'SELECTED_IN_PROCESS_CALL_RETURN_WITH_SELECTED_FULL_AUTHORITATIVE_BOUNDARIES'", "'SELECTED_IN_PROCESS_RETURNS_AND_AUTHORITATIVE_BOUNDARIES; BOUNDED_STRONG_REF_LRU; NOT_ALL_MUTATIONS'")
target.write_text(s)
print(target,len(s))