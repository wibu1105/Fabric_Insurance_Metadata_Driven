# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "5bcf29cf-7d4a-4083-8f1c-eb1b7d18f215",
# META       "default_lakehouse_name": "Rookie2Engineer_Lakehouse",
# META       "default_lakehouse_workspace_id": "68b1d404-ae48-4728-b5a6-bbdef89657cd",
# META       "known_lakehouses": [
# META         {
# META           "id": "1abd17a2-112c-4390-a066-25015003935f"
# META         },
# META         {
# META           "id": "5bcf29cf-7d4a-4083-8f1c-eb1b7d18f215"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# --- CONFIGURATION (Use exact GUID strings from browser address bars) ---
SRC_LAKEHOUSE = "Rookie2Engineer_Lakehouse"
SRC_WORKSPACE_ID = "5db1b4b5-9a8b-4bf9-808d-ed9af21bd9a8"  # E.g., 'a1b2c3d4-e5f6-...'

TGT_LAKEHOUSE = "Rookie2Engineer_Lakehouse"
TGT_WORKSPACE_ID = "68b1d404-ae48-4728-b5a6-bbdef89657cd"  # E.g., 'z9y8x7w6-v5u4-...'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import notebookutils

def reset_and_clone_lakehouse(source_lh_name: str, source_ws_id: str, target_lh_name: str, target_ws_id: str):
    """
    Clones a multi-schema lakehouse completely across workspaces by dynamically
    detecting schema folders and copying nested Delta tables.
    """
    print(f"--- Starting Schema-Aware Path Sync: {source_lh_name} -> {target_lh_name} ---")
    
    try:
        source_lh_meta = notebookutils.mssparkutils.lakehouse.get(source_lh_name, source_ws_id)
        target_lh_meta = notebookutils.mssparkutils.lakehouse.get(target_lh_name, target_ws_id)
        
        source_base = source_lh_meta["properties"]["abfsPath"]
        target_base = target_lh_meta["properties"]["abfsPath"]
    except Exception as e:
        print(f"Error fetching Lakehouse metadata: {e}")
        raise e

    # ----------------------------------------------------
    # 1. PROCESS TABLES (WITH MULTI-SCHEMA SUPPORT)
    # ----------------------------------------------------
    source_tables_path = f"{source_base}/Tables"
    target_tables_path = f"{target_base}/Tables"
    
    def sync_directory_explorer(relative_path=""):
        src_current_dir = f"{source_tables_path}/{relative_path}".rstrip("/")
        tgt_current_dir = f"{target_tables_path}/{relative_path}".rstrip("/")
        
        try:
            items = notebookutils.mssparkutils.fs.ls(src_current_dir)
        except Exception:
            return # Empty folder or inaccessible path
            
        # If a directory contains '_delta_log', it is a table, not a schema folder
        is_delta_table = any(item.name == "_delta_log" for item in items)
        
        if is_delta_table:
            print(f"Syncing Delta Table: {relative_path}")
            df = spark.read.format("delta").load(src_current_dir)
            df.write.format("delta").mode("overwrite").save(tgt_current_dir)
        else:
            # It's a schema folder (like 'audit' or 'dbo'), recurse deeper to find actual tables
            for item in items:
                if item.isDir and not item.name.startswith("_"):
                    next_relative_path = f"{relative_path}/{item.name}".lstrip("/")
                    sync_directory_explorer(next_relative_path)

    print("Scanning for schemas and tables...")
    sync_directory_explorer("")
    print("--- Tables Sync Completed Successfully ---")

    # ----------------------------------------------------
    # 2. PROCESS FILES DIRECTORY (Raw Storage)
    # ----------------------------------------------------
    source_files_path = f"{source_base}/Files"
    target_files_path = f"{target_base}/Files"
    
    try:
        notebookutils.mssparkutils.fs.rm(target_files_path, recurse=True)
    except Exception:
        pass 
        
    try:
        notebookutils.mssparkutils.fs.cp(source_files_path, target_files_path, recurse=True)
        print("--- Files Sync Completed Successfully ---")
    except Exception as e:
        print(f"Files directory empty or failed to copy: {e}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

reset_and_clone_lakehouse(
    source_lh_name=SRC_LAKEHOUSE,
    source_ws_id=SRC_WORKSPACE_ID,
    target_lh_name=TGT_LAKEHOUSE,
    target_ws_id=TGT_WORKSPACE_ID
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
