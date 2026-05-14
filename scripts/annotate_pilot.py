#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

LABEL_CHOICES={"1":"Preserved","2":"Authorized Transformation","3":"Inferred Extension","4":"Unresolved Gap","5":"Suspicious Drift","6":"Critical Distortion"}
RISK_FLAG_CHOICES={"a":"claim_strength_inflation","b":"uncertainty_loss","c":"responsibility_shift","d":"value_simplification","e":"institutional_implication_loss","f":"context_drift","g":"theoretical_reduction"}
CRITICALITY_CHOICES={"1":"low","2":"medium","3":"high"}


def parse_args(argv:list[str]|None=None)->argparse.Namespace:
    p=argparse.ArgumentParser(description="Japanese-first RDE annotation CLI")
    p.add_argument("--input",default="data/pilot_30.jsonl")
    p.add_argument("--output",default="data/annotations/annotations.jsonl")
    p.add_argument("--annotator",default="anonymous")
    p.add_argument("--no-resume",action="store_true")
    p.add_argument("--overwrite",action="store_true")
    return p.parse_args(argv)


def load_jsonl(path:Path)->list[dict]:
    records=[]
    if not path.exists():
        return records
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line=line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_annotated_ids(output_path:Path)->set[str]:
    return {str(r["id"]) for r in load_jsonl(output_path) if "id" in r}


def append_annotation(path:Path,record:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as fh:
        fh.write(json.dumps(record,ensure_ascii=False)+"\n")


def prompt_choice(title:str,choices:dict[str,str])->str:
    print(f"\n{title}")
    for k,v in choices.items():
        print(f" {k}) {v}")
    while True:
        raw=input("> ").strip()
        if raw in choices:
            return choices[raw]
        print("無効な入力です")


def prompt_flags()->list[str]:
    print("\nRisk flags (例: ab / Enterで空)")
    for k,v in RISK_FLAG_CHOICES.items():
        print(f" {k}) {v}")
    raw=input("> ").strip().replace(",","").replace(" ","")
    if not raw:
        return []
    result=[]
    for ch in raw:
        if ch in RISK_FLAG_CHOICES and RISK_FLAG_CHOICES[ch] not in result:
            result.append(RISK_FLAG_CHOICES[ch])
    return result


def main(argv:list[str]|None=None)->None:
    args=parse_args(argv)
    input_path=Path(args.input)
    output_path=Path(args.output)

    if args.no_resume and args.overwrite:
        print("--no-resume と --overwrite は同時指定できません",file=sys.stderr)
        sys.exit(1)

    if args.overwrite and output_path.exists():
        output_path.unlink()

    records=load_jsonl(input_path)
    done=set() if (args.no_resume or args.overwrite) else load_annotated_ids(output_path)
    pending=[r for r in records if str(r.get("id")) not in done]

    if not pending:
        print("すべてのサンプルは既に注釈済みです。")
        print(f"\n完了。新規注釈数: 0 件 → {output_path}")
        return

    count=0
    for idx,record in enumerate(pending,start=1):
        print("\n"+"─"*60)
        print(f"[{idx}/{len(pending)}] {record.get('id')}")
        print("\n【ソース】")
        print(record.get("source_ja") or record.get("source"))
        print("\n【出力】")
        print(record.get("output_ja") or record.get("output"))

        label=prompt_choice("ラベルを選択",LABEL_CHOICES)
        flags=prompt_flags()
        criticality=prompt_choice("criticalityを選択",CRITICALITY_CHOICES)
        explanation=input("\n説明(日本語): ").strip()

        annotation={
            "id":record["id"],
            "human_annotation":label,
            "risk_flags":flags,
            "criticality":criticality,
            "explanation_ja":explanation,
            "annotator":args.annotator,
            "annotated_at":datetime.now(tz=UTC).isoformat(),
        }
        append_annotation(output_path,annotation)
        count+=1

    print(f"\n完了。新規注釈数: {count} 件 → {output_path}")


if __name__=="__main__":
    main()
