from __future__ import annotations

import random, hashlib
from sqlalchemy.orm import Session
from repositories import question_repo, exam_repo
from utils.mix_utils import mix_exam
from models.exam import Upload
from utils.csv_utils import sniff_and_read

def norm_subject(s: str | None) -> str:
    if not s: return "math"
    s = s.strip().lower()
    if s in ("toán","toan","math"): return "math"
    if s in ("văn","van","literature"): return "literature"
    if s in ("anh","english","tiếng anh","tieng anh"): return "english"
    return "math"

def upload_bank(db: Session, subject: str, filename: str, file_bytes: bytes):
    rows = sniff_and_read(file_bytes)
    # chuyển "options" -> list để lưu DB
    for r in rows:
        r["options_list"] = [x.strip() for x in (r["options"] or "").split("||")] if r["options"] else []
    question_repo.replace_subject_questions(db, subject, rows)
    # lưu bản CSV thô để audit
    db.add(Upload(subject=subject, filename=filename, csv_text=file_bytes.decode("utf-8","ignore")))
    db.commit()
    return {"ok": True, "count": len(rows)}

def preview(db: Session, subject: str, n_questions:int, n_versions:int, seed:int|None,
            shuffle_qs:bool, shuffle_opts:bool, difficulty_quotas:dict|None):
    bank = [dict(
        ext_id=q.ext_id, text=q.text, options=q.options, answer=q.answer,
        points=q.points, topic=q.topic, difficulty=q.difficulty
    ) for q in question_repo.get_bank_by_subject(db, subject)]
    if not bank: raise ValueError("Ngân hàng rỗng")
    base_seed = seed if seed is not None else random.randint(1, 10**9)
    versions=[]
    for v in range(1, n_versions+1):
        rng = random.Random(base_seed + v)
        exam = mix_exam(bank, n_questions, shuffle_opts, shuffle_qs, rng, difficulty_quotas)
        versions.append({"version": v, "questions": [
            {"id": q["id"], "text": q["text"], "options": q["options"], "points": q["points"]} for q in exam
        ]})
    return {"bank_size": len(bank), "versions": versions}

def start_exam(db: Session, student_code: str, subject: str,
               req_cfg: dict, published_cfg: dict | None):
    # chọn cấu hình
    if published_cfg:
        cfg = published_cfg
        n_versions = int(cfg.get("n_versions") or 1)
        base_seed = cfg.get("seed")
        if n_versions < 1: n_versions = 1
        if base_seed is not None:
            h = hashlib.md5(f"{student_code}-{base_seed}".encode("utf-8")).hexdigest()
            version = (int(h,16) % n_versions) + 1
            seed = int(base_seed) + version
        else:
            version = random.randint(1, n_versions)
            seed = random.randint(1, 10**9)
        shuffle_qs = bool(cfg.get("shuffle_questions", True))
        shuffle_opts = bool(cfg.get("shuffle_options", True))
        n_questions = int(cfg.get("n_questions"))
        difficulty_quotas = cfg.get("difficulty_quotas")
    else:
        version = None
        seed = req_cfg.get("seed")
        n_questions = req_cfg.get("n_questions") or 0
        shuffle_qs = bool(req_cfg.get("shuffle_questions", True))
        shuffle_opts = bool(req_cfg.get("shuffle_options", True))
        difficulty_quotas = None

    # build đề từ DB
    bank = [dict(
        ext_id=q.ext_id, text=q.text, options=q.options, answer=q.answer,
        points=q.points, topic=q.topic, difficulty=q.difficulty
    ) for q in question_repo.get_bank_by_subject(db, subject)]
    rng = random.Random(seed)
    mixed = mix_exam(bank, n_questions, shuffle_opts, shuffle_qs, rng, difficulty_quotas)

    # tách questions/answer_key
    questions=[]; key={}
    total=0
    for q in mixed:
        questions.append({"id": q["id"], "text": q["text"], "options": q["options"], "points": q["points"]})
        key[str(q["id"])] = q["answer"]
        total += int(q["points"])
    # lưu session vào DB
    session_id = exam_repo.create_session(db, student_code, subject, version, total, questions, key)
    return {"session_id": session_id, "questions": questions, "version": version, "subject": subject}

def submit_exam(db: Session, session_id: int, answers: dict):
    sess = exam_repo.get_session(db, session_id)
    if not sess: raise ValueError("Không tìm thấy phiên thi")
    key = sess.answer_key or {}
    total = int(sess.total_points or 0)
    score=0; details=[]
    for q in (sess.questions or []):
        qid = str(q["id"])
        correct = (key.get(qid) or "").strip().upper()
        chosen  = (answers.get(qid) or "").strip().upper()
        ok = bool(correct and chosen and correct[:1]==chosen[:1])
        pts = int(q.get("points",1))
        if ok: score += pts
        details.append({"id": qid, "chosen": chosen[:1], "correct": correct[:1], "points": pts,
                        "earned_points": pts if ok else 0})
    exam_repo.create_submission(db, session_id, sess.student_code, score, total, answers, details)
    return {"session_id": session_id, "score": score, "total_points": total}
