#!/usr/bin/env python3
"""法考知识助手 - 数据查询工具"""

import json
import os
import sys
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def load_data():
    """加载所有数据文件"""
    with open(os.path.join(DATA_DIR, "knowledge_tree.json"), "r", encoding="utf-8") as f:
        tree = json.load(f)
    with open(os.path.join(DATA_DIR, "questions_all.json"), "r", encoding="utf-8") as f:
        questions_data = json.load(f)
    with open(os.path.join(DATA_DIR, "stats.json"), "r", encoding="utf-8") as f:
        stats = json.load(f)
    return tree, questions_data, stats

def get_subjects():
    """列出所有科目"""
    tree, _, stats = load_data()
    result = []
    for subj in tree["subjects"]:
        sid = subj["id"]
        name = subj["name"]
        ch_count = len(subj["chapters"])
        # 统计该科目题目数
        q_count = 0
        if sid in stats.get("subject_details", {}):
            q_count = stats["subject_details"][sid].get("count", 0)
        result.append({"id": sid, "name": name, "chapters": ch_count, "questions": q_count})
    return result

def get_knowledge(subject_id=None, chapter_id=None, section_id=None):
    """查询知识点树，支持逐级下钻"""
    tree, _, _ = load_data()
    
    for subj in tree["subjects"]:
        if subject_id and subj["id"] != subject_id:
            continue
        
        result = {"id": subj["id"], "name": subj["name"], "paper": subj.get("paper", ""), "chapters": []}
        
        for ch in subj["chapters"]:
            if chapter_id and ch["id"] != chapter_id:
                continue
            
            ch_info = {"id": ch["id"], "name": ch["name"], "sections": []}
            
            for sec in ch.get("sections", []):
                if section_id and sec["id"] != section_id:
                    continue
                
                sec_info = {"id": sec["id"], "name": sec["name"], "knowledge_points": []}
                
                for kp in sec.get("knowledge_points", []):
                    sec_info["knowledge_points"].append({
                        "id": kp["id"],
                        "name": kp["name"],
                        "description": kp.get("description", ""),
                        "importance": kp.get("importance", ""),
                        "related_laws": kp.get("related_laws", [])
                    })
                
                ch_info["sections"].append(sec_info)
            result["chapters"].append(ch_info)
        
        if subject_id:
            return result
    
    # 如果没指定subject_id，返回概览
    if not subject_id:
        all_subjects = []
        for subj in tree["subjects"]:
            subj_brief = {
                "id": subj["id"],
                "name": subj["name"],
                "chapter_count": len(subj["chapters"]),
                "total_sections": sum(len(ch.get("sections", [])) for ch in subj["chapters"]),
                "total_kps": sum(
                    len(sec.get("knowledge_points", []))
                    for ch in subj["chapters"]
                    for sec in ch.get("sections", [])
                )
            }
            all_subjects.append(subj_brief)
        return {"subjects": all_subjects, "total_subjects": len(all_subjects)}
    
    return {"error": f"未找到科目: {subject_id}"}

def search_questions(subject=None, year=None, question_type=None, difficulty=None, keyword=None, knowledge_point_id=None, limit=20):
    """检索真题"""
    _, qdata, _ = load_data()
    questions = qdata["questions"]
    
    results = []
    for q in questions:
        # 过滤条件
        if subject and q.get("subject") != subject:
            continue
        if year and q.get("year") != year:
            continue
        if question_type and q.get("question_type") != question_type:
            continue
        if difficulty and q.get("difficulty") != difficulty:
            continue
        if knowledge_point_id and knowledge_point_id not in q.get("knowledge_point_ids", []):
            continue
        if keyword and keyword not in q.get("content", "") and not any(keyword in str(v) for v in q.get("options", {}).values()):
            continue
        
        results.append({
            "id": q["id"],
            "year": q["year"],
            "subject": q["subject"],
            "question_type": q["question_type"],
            "content": q["content"],
            "options": q["options"],
            "answer": q.get("answer", ""),
            "analysis": q.get("analysis", ""),
            "difficulty": q.get("difficulty", ""),
            "knowledge_point_ids": q.get("knowledge_point_ids", []),
            "source": q.get("source", "")
        })
        
        if len(results) >= limit:
            break
    
    return {
        "total_matched": len(results),
        "limit": limit,
        "questions": results
    }

def get_stats():
    """获取统计数据"""
    _, _, stats = load_data()
    return stats

def analyze_knowledge_points(subject=None):
    """分析知识点考查频率"""
    _, qdata, _ = load_data()
    questions = qdata["questions"]
    
    # 统计每个知识点的出现次数
    kp_counter = Counter()
    kp_by_year = {}
    
    for q in questions:
        for kp_id in q.get("knowledge_point_ids", []):
            if subject and not kp_id.startswith(subject.split("_")[0]):
                # 简单前缀匹配过滤
                pass
            kp_counter[kp_id] += 1
            year = q.get("year")
            if year:
                if kp_id not in kp_by_year:
                    kp_by_year[kp_id] = Counter()
                kp_by_year[kp_id][year] += 1
    
    # 构建结果
    top_kps = []
    for kp_id, count in kp_counter.most_common(50):
        top_kps.append({
            "knowledge_point_id": kp_id,
            "question_count": count,
            "by_year": dict(kp_by_year.get(kp_id, {}))
        })
    
    return {
        "total_kps_with_questions": len(kp_counter),
        "top_knowledge_points": top_kps
    }

def find_kp_name(kp_id):
    """根据知识点ID查找知识点名称"""
    tree, _, _ = load_data()
    for subj in tree["subjects"]:
        for ch in subj["chapters"]:
            for sec in ch.get("sections", []):
                for kp in sec.get("knowledge_points", []):
                    if kp["id"] == kp_id:
                        return {"id": kp_id, "name": kp["name"], "subject": subj["name"], "chapter": ch["name"], "section": sec["name"]}
    return {"id": kp_id, "name": "未知知识点"}

def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <command> [args...]")
        print("命令: subjects, knowledge [subject_id] [chapter_id] [section_id], search [options], stats, analyze [subject]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "subjects":
        result = get_subjects()
    elif command == "knowledge":
        subject_id = sys.argv[2] if len(sys.argv) > 2 else None
        chapter_id = sys.argv[3] if len(sys.argv) > 3 else None
        section_id = sys.argv[4] if len(sys.argv) > 4 else None
        result = get_knowledge(subject_id, chapter_id, section_id)
    elif command == "search":
        kwargs = {}
        i = 2
        while i < len(sys.argv):
            key = sys.argv[i]
            if key.startswith("--"):
                param = key[2:]
                val = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
                if param == "limit":
                    val = int(val)
                elif param == "year":
                    val = int(val)
                kwargs[param] = val
                i += 2
            else:
                i += 1
        result = search_questions(**kwargs)
    elif command == "stats":
        result = get_stats()
    elif command == "analyze":
        subject = sys.argv[2] if len(sys.argv) > 2 else None
        result = analyze_knowledge_points(subject)
    elif command == "kp_name":
        kp_id = sys.argv[2] if len(sys.argv) > 2 else ""
        result = find_kp_name(kp_id)
    else:
        result = {"error": f"未知命令: {command}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
