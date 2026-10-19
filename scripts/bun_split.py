#!/usr/bin/env python3
"""Split the module graph out of a Bun single-file executable (`bun build --compile`).

Reads the `.bun` ELF section (extract it first with
`objcopy -O binary --only-section=.bun <exe> graph.bun`) and writes every embedded file
under an output directory, plus an index JSON. Layout confirmed against
`src/standalone_graph/StandaloneModuleGraph.zig` @ bun-v1.3.14 and the Rust rewrite
`StandaloneModuleGraph.rs` @ bun-v1.4.3 (harness-artifacts/01 §1.1):

    section = u64 byte_count | data... | Offsets(32 B) | "\\n---- Bun! ----\\n"
    Offsets = { byte_count: u64, modules: {off,len}, entry_point_id: u32,
                compile_exec_argv: {off,len}, flags: u32 }           # offsets from data start
    record  = 52 B: name, contents, sourcemap, bytecode, module_info,
                    bytecode_origin_path (StringPointer x6) + encoding, loader,
                    module_format, side (u8 x4)

Nothing is executed. The extracted files are vendor code: keep them out of version control.
"""
import argparse, json, os, struct, sys

FLAGS_1_4_3 = ["DISABLE_DEFAULT_ENV_FILES", "DISABLE_AUTOLOAD_BUNFIG", "DISABLE_AUTOLOAD_TSCONFIG",
               "DISABLE_AUTOLOAD_PACKAGE_JSON", "SOURCE_TEXT_CONTIGUOUS", "HAS_SOURCE_HASHES",
               "HAS_BUILTIN_BYTECODE", "HAS_BYTECODE_STRING_TABLE", "HAS_STARTUP_MODULE_COUNT",
               "HAS_MODULE_INFO_STRING_TABLE", "CROSS_COMPILED_BYTECODE", "HAS_PRELINKED_MODULE_GRAPH",
               "HAS_RUNTIME_OPTIONS", "HAS_LINKED_BYTECODE_PAYLOAD"]
TRAILER = b"\n---- Bun! ----\n"
REC = 52

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("section", help="raw .bun section bytes (objcopy output)")
    ap.add_argument("outdir", help="directory to write modules into (created)")
    ap.add_argument("--no-write", action="store_true", help="only print the index summary")
    a = ap.parse_args()
    raw = open(a.section, "rb").read()
    if not raw.endswith(TRAILER):
        sys.exit("not a Bun module graph: trailer missing")
    hdr = struct.unpack("<Q", raw[:8])[0]
    b = raw[8:]
    byte_count, mod_off, mod_len, entry_id, argv_off, argv_len, flags = struct.unpack("<QIIIIII", b[-48:-16])
    if mod_len % REC:
        sys.exit(f"module table length {mod_len} is not a multiple of {REC}")
    n = mod_len // REC
    index, bad = [], 0
    os.makedirs(a.outdir, exist_ok=True)
    for i in range(n):
        u = struct.unpack("<13I", b[mod_off + i * REC: mod_off + (i + 1) * REC])
        name = b[u[0]:u[0] + u[1]].decode("utf-8", "replace")
        if not name.startswith("/$bunfs/"):
            bad += 1
            continue
        rel = name.replace("/$bunfs/root/", "")
        rec = {"i": i, "name": rel, "bytes": u[3], "sourcemap_bytes": u[5], "bytecode_bytes": u[7],
               "module_info_bytes": u[9], "bytecode_origin_path": b[u[10]:u[10] + u[11]].decode("utf-8", "replace") if u[11] else "",
               "encoding": u[12] & 0xFF, "loader": (u[12] >> 8) & 0xFF, "module_format": (u[12] >> 16) & 0xFF,
               "side": (u[12] >> 24) & 0xFF, "entry": i == entry_id}
        index.append(rec)
        if not a.no_write:
            p = os.path.join(a.outdir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(b[u[2]:u[2] + u[3]])
            if u[5]:
                with open(p + ".map", "wb") as f:
                    f.write(b[u[4]:u[4] + u[5]])
    with open(os.path.join(a.outdir, "_index.json"), "w") as f:
        json.dump({"header_len": hdr, "byte_count": byte_count, "entry_point_id": entry_id,
                   "compile_exec_argv": b[argv_off:argv_off + argv_len].decode("utf-8", "replace"),
                   "flags": flags, "flags_1_4_3": [nm for k, nm in enumerate(FLAGS_1_4_3) if flags >> k & 1],
                   "modules": index}, f, indent=0)
    js = sum(1 for r in index if r["name"].endswith(".js") or r["entry"])
    bc = sum(1 for r in index if r["bytecode_bytes"])
    entry = next((r["name"] for r in index if r["entry"]), None)
    print(f"modules={n} unresolved={bad} js={js} with_bytecode={bc} entry={entry} flags={flags:#x}")

if __name__ == "__main__":
    main()
