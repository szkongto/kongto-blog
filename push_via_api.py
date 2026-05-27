"""Push via GitHub Git Database API using temp files for large payloads."""
import json, subprocess, sys, os, base64, tempfile

REPO = "szkongto/kongto-blog"
BRANCH = "main"

def gh(*args):
    r = subprocess.run(["gh", "api"] + list(args), capture_output=True, timeout=60)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace")
        print(f"gh error: {err}", file=sys.stderr)
        return None
    return json.loads(r.stdout.decode("utf-8"))

def main():
    # Get remote HEAD
    data = gh(f"repos/{REPO}/git/ref/heads/{BRANCH}")
    if not data:
        print("Failed to get remote HEAD", file=sys.stderr)
        sys.exit(1)
    remote_head_sha = data["object"]["sha"]
    print(f"Remote HEAD: {remote_head_sha}")

    # Get local HEAD
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
    local_sha = r.stdout.decode("utf-8").strip()
    print(f"Local HEAD: {local_sha}")

    if local_sha == remote_head_sha:
        print("Already up to date.")
        return

    # Get all objects from local HEAD
    r = subprocess.run(["git", "ls-tree", "-r", local_sha], capture_output=True)
    tree_entries = []
    for line in r.stdout.decode("utf-8").strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split(None, 3)
        tree_entries.append(parts)
    print(f"Total objects: {len(tree_entries)}")

    # Get remote tree recursively
    remote_tree_data = gh(f"repos/{REPO}/git/trees/{remote_head_sha}?recursive=1")
    existing = {}
    if remote_tree_data:
        for item in remote_tree_data.get("tree", []):
            if item["type"] == "blob":
                existing[item["path"]] = item["sha"]
    print(f"Remote has {len(existing)} existing blobs")

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Upload blobs
    tree_items = []
    for i, (mode, obj_type, obj_sha, raw_path) in enumerate(tree_entries):
        if obj_type != "blob":
            continue
        # Skip git Windows path duplicates (paths with embedded quotes/backslashes)
        if "\\" in raw_path or raw_path.startswith("\""):
            continue
        path = raw_path

        if path in existing and existing[path] == obj_sha:
            tree_items.append({"path": path, "mode": mode, "type": "blob", "sha": obj_sha})
            continue

        with open(path, "rb") as f:
            raw = f.read()
        try:
            text = raw.decode("utf-8")
            enc = "utf-8"
        except UnicodeDecodeError:
            text = base64.b64encode(raw).decode("ascii")
            enc = "base64"

        payload = json.dumps({"content": text, "encoding": enc})
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
            tf.write(payload)
            tfpath = tf.name

        try:
            data = gh(
                f"repos/{REPO}/git/blobs",
                "--method", "POST",
                "--input", tfpath,
            )
            if data:
                tree_items.append({"path": path, "mode": mode, "type": "blob", "sha": data["sha"]})
        finally:
            os.unlink(tfpath)

        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{len(tree_entries)} objects processed")

    print(f"Creating new tree with {len(tree_items)} items...")
    # Create tree in batches to avoid 502 from payload too large
    tree_sha = remote_tree_data["sha"]
    batch_size = 100
    new_tree = None
    for batch_start in range(0, len(tree_items), batch_size):
        batch = tree_items[batch_start:batch_start + batch_size]
        print(f"  Tree batch {batch_start//batch_size + 1}: {len(batch)} items (parent: {tree_sha[:8]}...)")
        payload = json.dumps({"tree": batch, "base_tree": tree_sha})
        tfpath = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
                tf.write(payload)
                tfpath = tf.name
            new_tree = gh(f"repos/{REPO}/git/trees", "--method", "POST", "--input", tfpath)
            if not new_tree:
                print(f"Batch {batch_start//batch_size + 1} failed")
                sys.exit(1)
            tree_sha = new_tree["sha"]
        finally:
            if tfpath:
                os.unlink(tfpath)

    new_tree_sha = tree_sha
    print(f"New tree: {new_tree_sha}")

    # Create commit
    r = subprocess.run(["git", "log", "-1", "--format=%B"], capture_output=True)
    msg = r.stdout.decode("utf-8").strip()

    payload = json.dumps({"message": msg, "tree": new_tree_sha, "parents": [remote_head_sha]})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        tf.write(payload)
        tfpath = tf.name
    try:
        commit_result = gh(f"repos/{REPO}/git/commits", "--method", "POST", "--input", tfpath)
    finally:
        os.unlink(tfpath)

    if not commit_result:
        print("Commit creation failed")
        sys.exit(1)
    commit_sha = commit_result["sha"]
    print(f"New commit: {commit_sha}")

    # Update ref
    payload = json.dumps({"sha": commit_sha, "force": False})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        tf.write(payload)
        tfpath = tf.name
    try:
        ref_result = gh(
            f"repos/{REPO}/git/refs/heads/{BRANCH}",
            "--method", "PATCH",
            "--input", tfpath,
        )
    finally:
        os.unlink(tfpath)

    if ref_result:
        print(f"Branch {BRANCH} updated to {commit_sha}")
        print("Done!")

if __name__ == "__main__":
    main()
