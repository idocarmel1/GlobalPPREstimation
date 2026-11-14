from pathlib import Path
import os,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
w=Path(__file__).resolve().parents[1]
r=w/'inputs/native_R_runtime/{app}'
print('namespace path length',len(str(r/'library/compiler/NAMESPACE')))
env={**os.environ,'R_ENABLE_JIT':'0','R_DEFAULT_PACKAGES':'NULL','LC_ALL':'English_United States.utf8','LANG':'en_US.UTF-8'}
expr='cat(R.home(),sep="\\n");print(.libPaths());print(file.exists(file.path(R.home(),"library/compiler/NAMESPACE")));print(warnings());print(Sys.getenv("R_HOME"));print(Sys.getlocale())'
q=subprocess.run([str(r/'bin/x64/Rscript.exe'),'--vanilla','-e',expr],capture_output=True,text=True,encoding='utf-8',errors='replace',env=env)
print(q.returncode);print(q.stdout);print(q.stderr)
(w/'qa/native_runtime_probe_fixed.log').write_text(q.stdout+'\nSTDERR\n'+q.stderr,encoding='utf-8')
