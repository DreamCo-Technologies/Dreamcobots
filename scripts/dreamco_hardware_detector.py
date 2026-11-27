#!/usr/bin/env python3
"""Report local hardware capacity; never launches training or downloads packages."""
import json, os, platform, sys
def detect():
 ram=None
 try: ram=round(os.sysconf("SC_PAGE_SIZE")*os.sysconf("SC_PHYS_PAGES")/1024**3,2)
 except (ValueError,OSError,AttributeError): pass
 gpu=None; vram=None
 try:
  import torch
  if torch.cuda.is_available():
   gpu=torch.cuda.get_device_name(0); vram=round(torch.cuda.get_device_properties(0).total_memory/1024**3,2)
  elif hasattr(torch.backends,"mps") and torch.backends.mps.is_available(): gpu="Apple Silicon MPS (unified memory; capacity reported as system RAM)"
 except ImportError: pass
 tiers=[]
 if (vram or 0)>=24 or (gpu and "Apple Silicon" in gpu and (ram or 0)>=32): tiers=["45m-edge","350m-workstation","1b-sovereign"]
 elif (vram or 0)>=8 or (gpu and "Apple Silicon" in gpu and (ram or 0)>=16): tiers=["45m-edge","350m-workstation"]
 elif (ram or 0)>=8: tiers=["45m-edge"]
 return {"schema":"dreamco.hardware_preflight.v1","platform":platform.platform(),"python":sys.version.split()[0],"cpu_count":os.cpu_count(),"system_ram_gb":ram,"gpu":gpu,"gpu_vram_gb":vram,"candidate_tiers":tiers,"selection_is_advisory":True,"training_started":False,"note":"Fit depends on sequence length, batch size, optimizer, quantization and framework overhead. Full pretraining may need substantially more memory."}
if __name__=="__main__": print(json.dumps(detect(),indent=2))
