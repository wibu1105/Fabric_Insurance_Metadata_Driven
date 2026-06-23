import json
import sys
from pathlib import Path
 
# Cac property tooltip ma API deploy (schema <= 2.5.0) khong dinh nghia
BAD_PROPERTIES = (
    "sentenceTemplate",
    "showSentenceFormat",
    "showChartSpecificTooltips",
    "showValuesInBold",
)
 
 
def _clean_visualtooltip(node):
    """
    Duyet de quy. Khi gap key 'visualTooltip' la mot list, xoa cac property xau
    trong 'properties' cua tung phan tu. Tra ve so property da xoa.
    Pham vi xoa duoc gioi han trong visualTooltip de khong dung property cung ten
    o noi khac (an toan).
    """
    removed = 0
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "visualTooltip" and isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        props = entry.get("properties")
                        if isinstance(props, dict):
                            for bad in BAD_PROPERTIES:
                                if bad in props:
                                    del props[bad]
                                    removed += 1
            else:
                removed += _clean_visualtooltip(value)
    elif isinstance(node, list):
        for item in node:
            removed += _clean_visualtooltip(item)
    return removed
 
 
def clean_file(path):
    """Lam sach 1 file visual.json. Tra ve so property da xoa (0 neu khong doi)."""
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [BO QUA] Khong doc duoc {path}: {e}")
        return 0
 
    removed = _clean_visualtooltip(data)
 
    if removed > 0:
        # Ghi lai (json.dump tu lo dau phay + cau truc, khong cat cut)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        # Validate lai: nem loi ngay neu vi mot ly do nao do file khong hop le
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
    return removed
 
 
def clean_all_visuals(repo_directory="."):
    """
    Duyet toan bo repo_directory, clean moi visual.json.
    Tra ve (so_file_da_clean, tong_property_da_xoa).
    """
    root = Path(repo_directory)
    if not root.exists():
        print(f"[clean_report_visuals] Khong tim thay thu muc: {repo_directory}")
        return (0, 0)
 
    visual_files = list(root.rglob("visual.json"))
    print(f"[clean_report_visuals] Tim thay {len(visual_files)} file visual.json trong '{repo_directory}'")
 
    cleaned_files = 0
    total_removed = 0
    for path in visual_files:
        removed = clean_file(path)
        if removed > 0:
            cleaned_files += 1
            total_removed += removed
            print(f"  [DA CLEAN] {path}  (xoa {removed} property)")
 
    if cleaned_files == 0:
        print("[clean_report_visuals] Khong co file nao can sua (tat ca da sach).")
    else:
        print(f"[clean_report_visuals] Da clean {cleaned_files} file, xoa tong {total_removed} property tooltip.")
    return (cleaned_files, total_removed)
 
 
if __name__ == "__main__":
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    clean_all_visuals(repo_dir)