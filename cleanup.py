import os

files_to_delete = [
    "_gen_logo.py",
    "analyze_design.py",
    "analyze_first_few.py",
    "analyze_selected.py",
    "create_assets.py",
    "design_analysis.md",
    "find_bug.py",
    "find_landing.py",
    "first_few_analysis.txt",
    "inspect_colors.py",
    "test_demo.py",
    "test_diag.py",
    "test_hf_token.py",
    "test_json.py",
    "test_live_glitch.py",
    "test_llm.py",
    "test_models.py",
    "test_outline_flow.py",
    "test_pptx.py",
    "test_slides.json"
]

print("🧹 Starting cleanup of unused debug/scratch files...")
deleted_count = 0

for file in files_to_delete:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"🗑️ Deleted: {file}")
            deleted_count += 1
        except Exception as e:
            print(f"⚠️ Error deleting {file}: {e}")

print(f"\n✨ Cleanup completed successfully! Removed {deleted_count} files.")
