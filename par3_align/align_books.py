import argparse
import tqdm
import os
import pickle
from pathlib import Path
from par3_align.utils import get_match_matrix, get_sentences, export_html, extract_match, get_book_size, read_file_with_trim

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', default="/data/kalpesh/better-paraphrases/data_new")
parser.add_argument('--output_file', default="aligned.pkl")
parser.add_argument('--output_html', default=None)
parser.add_argument('--long_books', action='store_true')
parser.add_argument('--overwrite', action='store_true')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

def recover_para_segmentations(aligned_data, gt_paras_sents, human_translator_data):
    """Recover paragraph-level data from original GT segmentation."""
    sents_covered = 0
    outputs = ""
    for p1, s1, src in zip(aligned_data["gt_paras"], gt_paras_sents, aligned_data["source_paras"]):
        num_sents = len(s1)
        outputs += f"<b>Source</> = {src}\n<b>Google Translate</> = {p1}\n"

        for translator, htd in human_translator_data.items():
            s2_sent_idx = []
            sent_aligns = extract_match(htd["match_matrix"], sents_covered, sents_covered + num_sents, readable=True)
            for salign in sent_aligns:
                s2_sent_idx.extend(salign['trans_idx'])
            s2_sent_idx = list(set(s2_sent_idx))
            s2_sent_idx.sort()

            p2_alignment = " ".join([htd['all_sents'][x] for x in s2_sent_idx])
            outputs += f"<b>{translator}</> = {p2_alignment}\n"

            aligned_data["translator_data"][translator]["translator_paras"].append(p2_alignment)
            aligned_data["translator_data"][translator]["sent_alignments"].append(sent_aligns)
        sents_covered += num_sents
        outputs += "\n\n"
    return aligned_data, outputs

def align_human_gt_sents(aligned_data, ht_files):
    human_translator_data = {}
    for ht_file in ht_files:
        ht_paras = read_file_with_trim(ht_file)
        ht_paras_sents = [get_sentences(x) for x in ht_paras]
        ht_sents = [x for s2 in ht_paras_sents for x in s2]

        match_matrix, _, _ = get_match_matrix(aligned_data["gt_sents"], ht_sents, verbose=args.verbose)
        human_translator_data[Path(ht_file).stem] = {
            "match_matrix": match_matrix,
            "all_sents": ht_sents
        }
        aligned_data["translator_data"][Path(ht_file).stem] = {
            "all_sents": ht_sents,
            "translator_paras": [],
            "sent_alignments": []
        }
    if args.verbose:
        print("match matrices computed")
    return human_translator_data, aligned_data

def get_files(book):
    """Get all files for a given book."""
    src_dir = os.path.join(args.dataset, book, "src_txts")
    trans_dir = os.path.join(args.dataset, book, "trans_txts")
    source_file = os.listdir(src_dir)
    assert len(source_file) == 1
    source_file = os.path.join(src_dir, source_file[0])

    all_translation_files = os.listdir(trans_dir)

    # google translation file
    gt_file = [tsl for tsl in all_translation_files if tsl.endswith("_gt.txt")]
    assert len(gt_file) == 1
    gt_file = os.path.join(trans_dir, gt_file[0])

    # human translation files
    ht_files = [
        os.path.join(trans_dir, tsl) for tsl in all_translation_files if not tsl.endswith("_gt.txt")
    ]
    return source_file, gt_file, ht_files

def main():
    books = [x for x in os.listdir(args.dataset) if not x.startswith(".")]
    book_size = [(book, int(get_book_size(os.path.join(args.dataset, book, "trans_txts")))) for book in books]
    book_size.sort(key=lambda x: x[1])

    for book, _ in tqdm.tqdm(book_size):
        print(book)
        # long books require the creation of a large matrix, so we skip them
        if not args.long_books and book in ["the_count_of_monte_cristo_fr", "les_miserables_fr", "romance_of_the_three_kingdoms_zh"]:
            continue
        # alignment data stored in args.output_file, skip if exists
        if os.path.exists(os.path.join(args.dataset, book, args.output_file)) and not args.overwrite:
            continue
        source_file, gt_file, ht_files = get_files(book)
        source_paras = read_file_with_trim(source_file)
        gt_paras = read_file_with_trim(gt_file)
        # Since google translations were done paragraph by paragraph, check there's a 1-1 match between source / GT paras
        assert len(source_paras) == len(gt_paras)

        gt_paras_sents = [get_sentences(x) for x in gt_paras]
        # Get rid of paragraph boundaries before alignment
        gt_sents = [x for s1 in gt_paras_sents for x in s1]
        if args.verbose:
            print(f"Total gt sentences = {len(gt_sents)}")

        aligned_data = {
            "source_paras": source_paras,
            "gt_paras": gt_paras,
            "gt_sents": gt_sents,
            "translator_data": {ht_file: {} for ht_file in ht_files}
        }

        # align each human translation sentence to a google translation sentence
        human_translator_data, aligned_data = align_human_gt_sents(aligned_data, ht_files)
        # recover paragraph-level data from original GT segmentation
        aligned_data, html_outputs = recover_para_segmentations(aligned_data, gt_paras_sents, human_translator_data)

        with open(os.path.join(args.dataset, book, args.output_file), "wb") as f:
            pickle.dump(aligned_data, f)

        # make output_html directory if it doesn't exist
        os.makedirs(args.output_html, exist_ok=True)
        if args.output_html:
            export_html(html_outputs, f"{args.output_html}/{book}")

if __name__ == "__main__":
    main()