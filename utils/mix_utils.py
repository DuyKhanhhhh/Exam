import random
from typing import List, Dict

DIFF_LEVELS = ("easy","medium","hard")

def split_opts(opts):
    if isinstance(opts, list): return opts
    return [x.strip() for x in (opts or "").split("||")] if opts else []

def count_by_diff(questions: List[dict]) -> Dict[str,int]:
    cnt = {d:0 for d in DIFF_LEVELS}
    for q in questions:
        d = q.get("difficulty","medium")
        cnt[d] = cnt.get(d,0)+1
    return cnt

def auto_quotas(n: int, avail: Dict[str,int]) -> Dict[str,int]:
    base = n // 3
    q = {d: base for d in DIFF_LEVELS}
    rem = n - base*3
    for d,_ in sorted(avail.items(), key=lambda x: -x[1]):
        if rem<=0: break
        q[d]+=1; rem-=1
    deficit=0
    for d in DIFF_LEVELS:
        if q[d] > avail.get(d,0):
            deficit += q[d]-avail.get(d,0)
            q[d] = avail.get(d,0)
    for d in sorted(DIFF_LEVELS, key=lambda k: avail.get(k,0)-q[k], reverse=True):
        if deficit<=0: break
        room = avail.get(d,0)-q[d]
        take = min(room, deficit)
        q[d]+=take; deficit-=take
    return q

def sample_by_diff(bank: List[dict], quotas: Dict[str,int], rng: random.Random):
    buckets = {d:[] for d in DIFF_LEVELS}
    for q in bank: buckets[q.get("difficulty","medium")].append(q)
    chosen=[]
    for d in DIFF_LEVELS:
        need = max(0, int(quotas.get(d,0)))
        pool = buckets.get(d,[])
        take = min(need, len(pool))
        if take>0: chosen += rng.sample(pool, take)
    while len(chosen) < sum(quotas.values()):
        rest=[q for q in bank if q not in chosen]
        if not rest: break
        chosen.append(rng.choice(rest))
    rng.shuffle(chosen)
    return chosen[:sum(quotas.values())]

def mix_exam(bank: List[dict], n_questions: int, shuffle_opts: bool, shuffle_qs: bool,
             rng: random.Random, difficulty_quotas=None):
    if n_questions<=0 or n_questions>len(bank): n_questions=len(bank)
    if difficulty_quotas:
        quotas = {k:max(0,int(v)) for k,v in (difficulty_quotas or {}).items()}
        total = sum(quotas.values()) or n_questions
        if total != n_questions:
            scale = n_questions / total
            quotas = {d:int(round(v*scale)) for d,v in quotas.items()}
            diff = n_questions - sum(quotas.values())
            for d in DIFF_LEVELS:
                if diff==0: break
                quotas[d] += 1 if diff>0 else -1
                diff += -1 if diff>0 else 1
    else:
        quotas = auto_quotas(n_questions, count_by_diff(bank))

    chosen = sample_by_diff(bank, quotas, rng)
    if shuffle_qs: rng.shuffle(chosen)

    out=[]
    for q in chosen:
        opts = split_opts(q["options"])
        ans  = (q["answer"] or "").strip().upper()
        if opts:
            idx = list(range(len(opts)))
            if shuffle_opts: rng.shuffle(idx)
            new_opts = [opts[i] for i in idx]
            new_ans  = ""
            if ans and ans[0].isalpha():
                ci = ord(ans[0])-65
                if 0<=ci<len(opts): new_ans = chr(65 + idx.index(ci))
        else:
            new_opts = opts; new_ans = ans
        out.append({
            "id": q["ext_id"],
            "text": q["text"],
            "options": new_opts,
            "answer": new_ans,
            "points": q["points"],
            "topic": q["topic"],
            "difficulty": q["difficulty"],
        })
    return out
