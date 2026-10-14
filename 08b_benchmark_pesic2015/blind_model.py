"""Eligibility gate only; no fibre prediction is authorised with incomplete inputs."""
from pathlib import Path
import runpy,hashlib
C=runpy.run_path(str(Path(__file__).with_name('common.py')));globals().update(C)
ref=REF/'musial_model.py'
save('blind_model_status.json',{'status':'SKIPPED_INCOMPLETE_AND_INCONSISTENT_INPUTS','reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),
'reasons':['Concrete tensile strength not independently measured; authors best-fit tensile strength is tuned and cannot enter a blind model.',
'Table 2 cover and Appendix B bar-centre coordinates conflict.',
'Measured steel elastic modulus and ultimate strain absent; appendix lists adopted finite element values rather than a complete measured steel curve.',
'Beam 3 initial damage unknown; an undamaged fibre model would not represent its initial state.'],
'model_tuned':False,'paper_predictions_are_not_our_blind_model':True})
