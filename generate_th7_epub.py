import os
import subprocess
import glob
import re
import shutil

# Configuration
base_dir = "/Users/peiwenyang/Development/expanse"
source_dir = os.path.join(base_dir, "the_expanse/无垠的太空(7)波斯波利斯崛起")
output_dir = os.path.join(base_dir, "the_expanse/中文电子书")
css_path = os.path.join(base_dir, "the_expanse/Styles/stylesheet.css")
output_filename = "无垠的太空(7).波斯波利斯崛起.epub"
output_path = os.path.join(output_dir, output_filename)

# Metadata
title = "无垠的太空(7): 波斯波利斯崛起"
author = "詹姆斯·S.A.·科里 (James S.A. Corey)"
language = "zh-CN"

def main():
    print(f"Generating EPUB: {output_path}")

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Gather input files
    # We use glob to find all expected markdown files.
    # The naming convention "th7_第XX章..." ensures they sort correctly alphabetically.
    # However, to be extra safe and follow the user's explicit list order is better if possible,
    # but here the filenames are well-structured (00-53), so sorting is reliable.
    
    search_pattern = os.path.join(source_dir, "th7_*.md")
    files = glob.glob(search_pattern)
    files.sort()

    # Filter out unwanted files
    # User requested to remove the file starting with "th7_尾声", which is likely a duplicate or misplaced epilogue
    # The correct epilogue is th7_第53章...
    files = [f for f in files if "th7_尾声" not in os.path.basename(f)]

    if not files:
        print("Error: No markdown files found in source directory.")
        return

    print(f"Found {len(files)} chapters.")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    # Construct pandoc command
    # We will run pandoc from source_dir so relative paths (like ../Images/sep.png) work.
    
    # Files are already sorted, we just need their basenames
    input_filenames = [os.path.basename(f) for f in files]

    cmd = [
        "pandoc",
        "-o", output_path, # output_path is absolute so this is fine
        f"--metadata=title:{title}",
        f"--metadata=author:{author}",
        f"--metadata=lang:{language}",
        "--toc",
        "--split-level=1", # Replace deprecated --epub-chapter-level
        f"--css={css_path}", # css_path is absolute so this is fine
        "--wrap=none"
    ]

    # Create temporary build directory
    build_dir = os.path.join(base_dir, "build_temp")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    print(f"Preparing build files in {build_dir}...")

    # Function to convert footnotes (adapted regarding user requirement)
    def convert_markdown(content, filename):
        match = re.search(r'th7_第(\d+)章', filename)
        if match:
            chap_id = match.group(1)
        else:
            if "尾声" in filename or "杜阿尔特" in filename:
                chap_id = "53"
            else:
                chap_id = "xx"

        definitions = {}
        def store_def(match):
            ref_id = match.group(1)
            text = match.group(2).strip()
            definitions[ref_id] = text
            return "" 

        # Capture definitions: [^1]: ...
        # Standard markdown footnotes
        content = re.sub(r'^\[\^(\d+)\]:(.+)$', store_def, content, flags=re.MULTILINE)

        def replace_ref(match):
            ref_id = match.group(1)
            if ref_id in definitions:
                n = int(ref_id)
                # Map 1..20 to circled numbers
                circled = chr(9311 + n) if 1 <= n <= 20 else f"({n})"
                return f'<span><a id="zhu{chap_id}_{ref_id}_a" href="#zhu{chap_id}_{ref_id}_b"><sup>{circled}</sup></a></span>'
            return match.group(0)

        # Replace refs: [^1]
        content = re.sub(r'\[\^(\d+)\]', replace_ref, content)

        # Remove existing headers or leftovers
        content = re.sub(r'^## 译注\s*$', '', content, flags=re.MULTILINE)
        content = content.strip()

        if definitions:
            sorted_ids = sorted(definitions.keys(), key=lambda x: int(x))
            
            # Use EXACT HTML format requested by user
            footer_html = '\n\n<h3 style="text-align: left; text-indent: 2em;" class="sigil_not_in_toc">译注</h3>\n'
            
            for ref_id in sorted_ids:
                text = definitions[ref_id]
                n = int(ref_id)
                circled = chr(9311 + n) if 1 <= n <= 20 else f"({n})"
                
                # Careful with Bold syntax inside definitions. 
                # The user's example: **Term**: Definition
                # We need to make sure the text from standard markdown is preserved or handled.
                # Since we extracted raw text from `[^1]: ...` which includes markdown, 
                # sticking it into the HTML context is mostly fine as Pandoc processes it?
                # NO. If we are injecting RAW HTML blocks, Pandoc might treat the content inside <p> as raw HTML too 
                # if we are not careful, or we rely on Pandoc to parse markdown inside block tags.
                # However, the user said "原样照抄即可" (copy exactly). 
                # The user text example: <p>...**被试（subject）**：...</p>
                # If we output `**...**` inside HTML, Pandoc usually handles markdown-in-html if enabled. 
                # But to be safe and match the reference behavior which seems to rely on this mixing:
                
                entry = f'<p><a id="zhu{chap_id}_{ref_id}_b" href="#zhu{chap_id}_{ref_id}_a">{circled}</a>{text}</p>\n'
                footer_html += entry
            
            content += footer_html
        
        return content

    # Process files
    input_files_for_pandoc = []
    
    # We rely on 'files' list populated earlier
    print(f"Processing {len(files)} files...")

    for fpath in files:
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Convert content
        new_content = convert_markdown(raw_content, fname)
        
        # Write to temp dir
        temp_path = os.path.join(build_dir, fname)
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        input_files_for_pandoc.append(os.path.basename(temp_path))

    # Add input files
    cmd.extend(input_files_for_pandoc)

    print(f"\nRunning pandoc from {build_dir}...")
    try:
        # Run in build_dir so relative paths to images might break if they assume source_dir?
        # The script defines css_path as absolute. 
        # But images: if markdown has `![](../Images/foo.png)`, valid from `source_dir`.
        # `build_dir` is `.../expanse/build_temp`. `source_dir` is `.../expanse/the_expanse/Translation...`
        # Wait, `source_dir` = `.../the_expanse/无垠的太空(7)波斯波利斯崛起`
        # If I put build_dir as sibling to `the_expanse`?
        # User defined `base_dir` = `/.../Development/expanse`
        # `source_dir` is deeper.
        # If I run from `build_dir`, `../Images` won't work if `build_dir` is in `base_dir`.
        # I should put `build_dir` INSIDE `the_expanse` folder or replicate structure?
        # Or just tell Pandoc where to find things?
        # Easiest: put `build_dir` inside `source_dir`.
        pass
    except Exception:
        pass

    # Re-evaluating build path to ensure relative links work
    # source_dir has images usually in `../Images`? 
    # Let's check where `stylesheet.css` is: `.../Styles/stylesheet.css`.
    # Structure seems to be:
    # the_expanse/
    #   Styles/
    #   Images/ (presumably)
    #   无垠的太空(7)波斯波利斯崛起/ (source_dir)
    #     th7_*.md
    
    # So if I make `build_dir` = `source_dir / "temp_build"`, then `../Images` works fine.
    
    if os.path.exists(os.path.join(source_dir, "temp_build")):
        shutil.rmtree(os.path.join(source_dir, "temp_build"))
    os.makedirs(os.path.join(source_dir, "temp_build"))
    build_dir = os.path.join(source_dir, "temp_build")
    
    # ... (loop to write files to build_dir) ...
    
    # (Redoing the loop logic in the actual replacement string below)

    for fpath in files:
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        new_content = convert_markdown(raw_content, fname)
        temp_path = os.path.join(build_dir, fname)
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        input_files_for_pandoc.append(fname) # Just filename, we run cwd=build_dir

    cmd.extend(input_files_for_pandoc)

    print(f"\nRunning pandoc from {build_dir}...")
    try:
        subprocess.run(cmd, check=True, cwd=build_dir)
        print("EPUB generation successful!")
        print(f"Output: {output_path}")
    except subprocess.CalledProcessError as e:
        print("EPUB generation failed.")
        print(e)
    finally:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

if __name__ == "__main__":
    main()
