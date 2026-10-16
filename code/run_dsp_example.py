"""Reproducible DSP illustration, NOT a REAPER run or a trained-model inference.
Synthetic test signals are intentionally not labelled as recorded vocals/music.
Run: python run_dsp_example.py --out ../output/dsp
"""
from __future__ import annotations
import argparse, hashlib, json, platform, sys
from pathlib import Path
import numpy as np
import soundfile as sf
import pedalboard
from pedalboard import Pedalboard, Gain, Compressor

def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x.astype(np.float64)))))
def db(x: float) -> float:
    return float(20*np.log10(max(x,1e-20)))
def process(x: np.ndarray, effects: list, sr: int) -> np.ndarray:
    return Pedalboard(effects)(np.ascontiguousarray(x.T,dtype=np.float32),sr,reset=True).T

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,default=Path('dsp'))
    args=parser.parse_args(); out=args.out;out.mkdir(parents=True,exist_ok=True)
    sr=48000; duration=36.; t=np.arange(int(sr*duration),dtype=np.float64)/sr
    rng=np.random.default_rng(20261013)
    # Different time-varying, bounded spectra, not synthesized human singing.
    e1=.45+.45*np.sin(2*np.pi*.63*t)**2
    v=e1*(.24*np.sin(2*np.pi*233*t)+.08*np.sin(2*np.pi*466*t)+.03*np.sin(2*np.pi*699*t))
    pulse=np.exp(-((t%.5)/.06))
    a=.16*np.sin(2*np.pi*73.416*t)+.055*np.sin(2*np.pi*146.832*t)+.07*pulse*np.sin(2*np.pi*55*t)
    a+=.005*rng.standard_normal(t.size)
    v=np.stack([v,v],axis=1).astype(np.float32)
    a=np.stack([a, .95*a+.015*np.sin(2*np.pi*440*t)],axis=1).astype(np.float32)
    # Gain envelope goes 0 -> plateau -> 0 within the authorized region.
    env=np.zeros(t.size);env[(t>=16.05)&(t<=31.95)]=1
    m=(t>16)&(t<16.05);env[m]=(t[m]-16)/.05
    m=(t>31.95)&(t<32);env[m]=(32-t[m])/.05
    # Constant Gain processors run on full tracks; envelope blending is linear in amplitude.
    # Only the plateau is used for Eq.(1), independent of the ramp interpolation mode.
    vg=process(v,[Gain(gain_db=1.5)],sr); ag=process(a,[Gain(gain_db=-1.5)],sr)
    A=(v+(vg-v)*env[:,None]+a).astype(np.float32)
    B=(v+a+(ag-a)*env[:,None]).astype(np.float32)
    base=(v+a).astype(np.float32)
    comp=lambda: Compressor(threshold_db=-18,ratio=4,attack_ms=10,release_ms=100)
    Ac=process(A,[comp()],sr);Bc=process(B,[comp()],sr)
    # Store and reread FLOAT WAVs to include output quantization in the check.
    arrays={'test_v':v,'test_band':a,'baseline':base,'linear_A':A,'linear_B':B,
            'compressed_A':Ac,'compressed_B':Bc}
    hashes={}
    for name,x in arrays.items():
        path=out/(name+'.wav');sf.write(path,x,sr,subtype='FLOAT')
        arrays[name],_=sf.read(path,dtype='float32',always_2d=True)
        hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    Bmatch=process(arrays['linear_B'],[Gain(gain_db=1.5)],sr)
    Bcmatch=process(arrays['compressed_B'],[Gain(gain_db=1.5)],sr)
    stable=(t>=16.05)&(t<31.95)
    residual=arrays['linear_A']-Bmatch
    residual_c=arrays['compressed_A']-Bcmatch
    def result(ref,res):
        return {'reference_rms':rms(ref[stable]),'residual_rms':rms(res[stable]),
                'residual_rms_dbfs':db(rms(res[stable])),
                'residual_relative_db':db(rms(res[stable])/rms(ref[stable])),
                'residual_peak':float(np.max(np.abs(res[stable])))}
    # Same-duration block-RMS trace; individual plots produced by separate visualization script.
    step=int(.1*sr);rows=[]
    for k in range(0,len(t)-step+1,step):
        sl=slice(k,k+step); rows.append([t[k]+.05,db(rms(residual[sl])),db(rms(residual_c[sl]))])
    np.savetxt(out/'residual_trace.csv',rows,delimiter=',',header='time_s,linear_residual_dbfs,compressed_residual_dbfs',comments='')
    data={'status':'executed locally using open-source Pedalboard; not REAPER; not model replication',
          'signal_kind':'deterministic synthetic diagnostic signals, not musical stems or human voice',
          'sample_rate':sr,'duration_s':duration,'dtype':'float32','file_subtype':'FLOAT',
          'seed':20261013,'stable_window_s':[16.05,31.95],
          'gain_db':1.5,'gamma':float(10**(1.5/20)),
          'compressor':{'threshold_db':-18,'ratio':4,'attack_ms':10,'release_ms':100},
          'linear':result(arrays['linear_A'],residual),
          'shared_compression':result(arrays['compressed_A'],residual_c),
          'versions':{'python':sys.version.split()[0],'platform':platform.platform(),
                      'numpy':np.__version__,'soundfile':sf.__version__,'pedalboard':pedalboard.__version__},
          'sha256':hashes,
          'limitations':['Pedalboard compressor is not ReaComp and does not reproduce all ReaComp settings.',
                         'No trained AI system, subjective listening test, or musical-quality evaluation was run.',
                         'Only the stable window tests the constant-gain identity.','Not a universal residual threshold.']}
    assert data['linear']['residual_peak']<1e-6
    assert data['shared_compression']['residual_rms']>100*data['linear']['residual_rms']
    (out/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    excerpt=out/'excerpts';excerpt.mkdir(exist_ok=True)
    for name in ['test_v','test_band','linear_A','linear_B','compressed_A','compressed_B']:
        sf.write(excerpt/(name+'_20-22s.wav'),arrays[name][20*sr:22*sr],sr,subtype='FLOAT')
    print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
