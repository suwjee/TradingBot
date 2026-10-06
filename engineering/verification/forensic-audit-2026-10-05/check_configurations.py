"""Public CLI enablement, output projection, direction, and range consistency."""
from pathlib import Path
import itertools, json, subprocess
from run_raw_matrix import OUT, command

def main():
    raw=json.loads((OUT/'raw-registry.json').read_text(encoding='utf-8'))[6]
    root=OUT/'configurations'
    root.mkdir(exist_ok=True)
    cases=[]
    def execute(name,cmd):
        completed=subprocess.run(cmd,capture_output=True,timeout=180)
        (root/(name+'.stdout.json')).write_bytes(completed.stdout)
        (root/(name+'.stderr.log')).write_bytes(completed.stderr)
        result=json.loads(completed.stdout)
        result.pop('timings',None)
        case={'name':name,'command':cmd,'exitCode':completed.returncode,
              'execution':'PASS' if completed.returncode==0 else 'FAIL'}
        if completed.returncode: case['error']=result
        cases.append(case)
        return result
    baseline=execute('both',command(Path(raw['path']),30,raw['first'],raw['last']))
    for direction in ('bullish','bearish'):
        result=execute(direction,command(Path(raw['path']),30,raw['first'],raw['last'],direction))
        cases[-1]['sameDirectionAsBoth']='PASS' if result['directions'][direction]==baseline['directions'][direction] else 'FAIL'
    cmd=command(Path(raw['path']),30,raw['first'],raw['last'])
    cmd.remove('--bridge-output')
    legacy=execute('legacy-without-projection',cmd)
    same=True
    for direction,body in baseline['directions'].items():
        same &= {k:v for k,v in body.items() if k!='bridgeOutput'}==legacy['directions'][direction]
    cases[-1]['legacyUnchangedByOptionalProjection']='PASS' if same else 'FAIL'
    for values in itertools.product(('enabled','disabled'),repeat=3):
        cmd=command(Path(raw['path']),30,raw['first'],raw['last'])
        for flag,value in zip(('blue-lines','a-zones','s-zones'),values): cmd += ['--'+flag,value]
        result=execute('toggle-'+''.join('1' if x=='enabled' else '0' for x in values),cmd)
        if cases[-1]['execution']=='PASS':
            cases[-1]['disabledPublicArrays']='PASS' if all(not body[stage] for body in result['directions'].values()
                for value,stage in zip(values,('blueLines','aZones','sZones')) if value=='disabled') else 'FAIL'
    for missing in ('e-engine','stopall-engine'):
        cmd=command(Path(raw['path']),30,raw['first'],raw['last'])
        i=cmd.index('--'+missing); del cmd[i:i+2]
        execute('without-'+missing,cmd)
    first=raw['first']+3600
    last=raw['last']-3600
    cmd=command(Path(raw['path']),30,first,last)
    ranged=execute('presentation-range',cmd)
    differences=[]
    for direction,body in baseline['directions'].items():
        for stage,field in [('reactions','firstTime'),('resets','time'),('blueLines','sourceTime'),('aZones','sourceTime'),
                            ('sZones','sourceTime'),('eZones','sourceTime'),('stopAlls','sourceTime')]:
            expected=[item for item in body[stage] if first//30*30<=item[field]<=last//30*30]
            actual=ranged['directions'][direction][stage]
            if actual!=expected: differences.append({'direction':direction,'stage':stage,'expectedCount':len(expected),'actualCount':len(actual)})
    cases[-1]['presentationRangeSameCalculatedObjects']='PASS' if not differences else 'FAIL'
    cases[-1]['differences']=differences
    (root/'manifest.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in c.items() if k!='command'} for c in cases],indent=2))

if __name__=='__main__': main()
