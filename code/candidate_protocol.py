"""Finite-candidate protocol checks. Numbers are analytical conditions, not listening data.
Python >=3.10, standard library only.
Usage: python candidate_protocol.py --output analytical_candidates.json
"""
from __future__ import annotations
import argparse, json, math, random
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class Candidate:
    id: int
    vocal_db: float
    band_db: float
    relative_db: float
    target_error_db: float
    protected_distance_db: float
    target_pass: bool
    protection_pass: bool
    D_P: float
    C_S: float
    C_theta: float
    J: float

def candidate_bank(target_db:float=1.5, target_tolerance:float=.2,
                   protection_tolerance:float=.2)->list[Candidate]:
    if target_tolerance<0 or protection_tolerance<=0:
        raise ValueError('Target tolerance must be nonnegative; cost normalization requires positive protection tolerance.')
    grid=[-.0 + k*.5 for k in range(-3,4)]
    settings=sorted(set((v,b) for v in grid for b in grid)|{(1.2,-.3),(1.4,-.1)})
    result=[]
    for i,(v,b) in enumerate(settings,1):
        relative=v-b;error=abs(relative-target_db);distance=abs(b)
        dp=distance/protection_tolerance
        cs=(int(v!=0)+int(b!=0))/2
        cp=(abs(v)+abs(b))/1.5
        result.append(Candidate(i,v,b,relative,error,distance,error<=target_tolerance+1e-10,
                     distance<=protection_tolerance+1e-10,dp,cs,cp,.6*dp+.2*cs+.2*cp))
    assert len(result)==51
    return result

def select(bank:list[Candidate],name:str,seed:int=20261015)->Candidate|None:
    g=[x for x in bank if x.target_pass]
    fm=[x for x in g if x.protection_pass]
    if name=='baseline':
        shuffled=bank[:];random.Random(seed).shuffle(shuffled)
        return next((x for x in shuffled if x.target_pass),None)
    if name=='operation':pool=g;key=lambda x:(.2*x.C_S+.2*x.C_theta,x.id)
    elif name=='protection':pool=fm;key=lambda x:(x.D_P,x.id)
    elif name=='full':pool=fm;key=lambda x:(x.J,x.id)
    else:raise ValueError(name)
    return min(pool,key=key) if pool else None

def listening_pass(target:int|None, protected:list[int|None], accepted:bool|None,
                   technical:bool)->bool|None:
    if not technical:return False
    if target is None or any(x is None for x in protected) or accepted is None:return None
    if not -3<=target<=3 or any(not 0<=x<=6 for x in protected if x is not None):
        raise ValueError('Score outside the preregistered scale.')
    return -1<=target<=1 and all(x<=2 for x in protected if x is not None) and accepted

def task_label(votes:list[bool|None],planned:int)->str:
    if planned<=0 or len(votes)>planned:raise ValueError('Invalid planned count.')
    valid=[v for v in votes if v is not None]
    if len(valid)<math.ceil(.8*planned):return 'insufficient_evidence'
    return 'accepted' if sum(valid)/len(valid)>=2/3 else 'not_accepted'

def self_test()->dict:
    bank=candidate_bank();a=next(x for x in bank if (x.vocal_db,x.band_db)==(1.5,0))
    d=next(x for x in bank if (x.vocal_db,x.band_db)==(1.4,-.1))
    b=next(x for x in bank if (x.vocal_db,x.band_db)==(0,-1.5))
    assert a.target_pass and a.protection_pass and d.target_pass and d.protection_pass
    assert b.target_pass and not b.protection_pass
    assert abs(a.J-.3)<1e-12 and abs(d.J-.7)<1e-12
    for target in (-1.5,-1,-.5,0,.5,1,1.5):
        result=select(candidate_bank(target),'full');assert result and result.target_pass and result.protection_pass
    zero=select(candidate_bank(0),'full');assert zero and zero.vocal_db==0 and zero.band_db==0
    assert listening_pass(0,[0,2],True,True) is True
    assert listening_pass(0,[0,3],True,True) is False
    assert listening_pass(0,[0,2],False,True) is False
    assert listening_pass(None,[0,2],True,True) is None
    assert task_label([True]*8+[False]*4,12)=='accepted'
    assert task_label([True]*8+[None]*4,12)=='insufficient_evidence'
    return {'candidate_count':51,'A_cost':a.J,'D_cost':d.J,'checks':'passed',
            'status':'analytical and scoring-rule unit tests only; no human ratings generated'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path('analytical_candidates.json'));args=ap.parse_args()
    bank=candidate_bank()
    data={'status':'conditional analytical results, not rendered or perceptual results','unit_tests':self_test(),
          'candidates':[asdict(x) for x in bank],
          'selectors':{key:asdict(x) if (x:=select(bank,key)) else None for key in ('baseline','operation','protection','full')}}
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2));print(json.dumps(data['unit_tests'],indent=2))
if __name__=='__main__':main()
