#!/usr/bin/env python3
"""Generate explicitly non-certified research catalogs and executable token examples."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from buddy.workbench.core import BytePairTokenizer,token_report
RL='Q-learning|SARSA|Expected SARSA|Double Q-learning|Monte Carlo control|TD(lambda)|Watkins Q(lambda)|DQN|Double DQN|Dueling DQN|Prioritized experience replay|Rainbow DQN|C51|QR-DQN|IQN|FQF|REINFORCE|A2C|A3C|TRPO|PPO|DDPG|TD3|SAC|TQC|REDQ|CQL|IQL|BCQ|AWAC'.split('|')
UPDATES='SGD|Momentum SGD|Nesterov momentum|AdaGrad|RMSProp|AdaDelta|Adam|AdamW|AdaMax|NAdam|RAdam|Adafactor|Lion|LAMB|LARS|Shampoo|K-FAC|Natural gradient|L-BFGS|SignSGD|Sophia|Muon|SAM|ASAM|Lookahead|Stochastic weight averaging|Exponential moving average|Gradient clipping|Gradient accumulation|Cosine learning-rate scheduling'.split('|')
EXAMPLES=['Hello world','hello hello hello','Café déjà vu','🙂🙂🙂','你好世界','مرحبا بالعالم','こんにちは','naïve résumé','a b c','abc','1234567890','3.14159265','user_id=42','{"ok":true}','SELECT id FROM users;','def add(a,b): return a+b','https://example.com/city','Chicago, Illinois','New York, NY','line one\nline two','one\tcolumn','  extra   spaces  ','customer_subscription_status','customerSubscriptionStatus','antidisestablishmentarianism','unbelievable','pretraining posttraining','🚀 launch ready','Yes. No. Maybe.','Summarize the attached evidence in three bullets.']
PATTERNS='Singleton|Builder|Factory Method|Adapter|Facade|Proxy|Decorator|Composite|Strategy|Observer|State|Command|Template Method|Chain of Responsibility|Iterator'.split('|')
def main():
    tok=BytePairTokenizer();tok.train(' '.join(EXAMPLES)*3)
    payload={'schema':'dreamco.workbench.curriculum.v1','rl_techniques':[{'name':n,'status':'research_reference_not_implemented','requires':['environment','reward_specification','baseline','heldout_evaluation','rights','budget','rollback']} for n in RL], 'weight_update_techniques':[{'name':n,'status':'adapter_required','production_ready':False} for n in UPDATES],'design_patterns':PATTERNS,'token_examples':[{'text':s,'byte_tokenizer':token_report(s),'trained_bpe':tok.inspect(s)} for s in EXAMPLES], 'notes':['No technique is universally best. Select by task and controlled experiments.','Do not penalize safe refusal, uncertainty disclosure, or asking necessary questions.','Freeze reward rubrics before evaluation; keep holdout tasks out of training.','A larger vocabulary requires compatible embeddings and evidence that quality/cost improve.'], 'references':['https://huggingface.co/docs/transformers/main/tokenizer_summary','https://huggingface.co/docs/trl/index','https://stable-baselines3.readthedocs.io/en/master/guide/algos.html']}
    out=ROOT/'website/data/workbench-curriculum.json';out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n');print(len(EXAMPLES),len(RL),len(UPDATES))
if __name__=='__main__':main()
