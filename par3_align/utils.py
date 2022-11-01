import subprocess
import spacy
import numpy as np
import tqdm
from par3_align.similarity.test_sim import find_similarity_matrix

nlp = spacy.load('en_core_web_sm')

def get_book_size(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du','-s', path]).split()[0].decode('utf-8')

def get_sentences(text):
    return [x.text for x in nlp(text).sents]

def read_file_with_trim(filename):
    with open(filename, 'r') as f:
        para_list = f.read().split("\n")
    if para_list[-1].strip() == '':
        para_list = para_list[:-1]
    return para_list

class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def postprocess(cls, input_str):
        input_str = input_str.replace("<h>", cls.HEADER)
        input_str = input_str.replace("<blue>", cls.OKBLUE)
        input_str = input_str.replace("<green>", cls.OKGREEN)
        input_str = input_str.replace("<yellow>", cls.WARNING)
        input_str = input_str.replace("<red>", cls.FAIL)
        input_str = input_str.replace("</>", cls.ENDC)
        input_str = input_str.replace("<b>", cls.BOLD)
        input_str = input_str.replace("<u>", cls.UNDERLINE)
        input_str = input_str.replace("<clean>", "")
        return input_str

def export_html(output, filename):
    """Export alignments to a readable HTML format."""
    with open("{}.txt".format(filename), "w") as f:
        f.write(Bcolors.postprocess(output) + "\n")
    subprocess.check_output("cat {0}.txt | par3_align/ansi2html.sh --palette=linux --bg=dark > {0}.html".format(filename), shell=True)
    subprocess.check_output("rm {}.txt".format(filename), shell=True)

def extract_match(mm, left_idx, right_idx, row_col='row', readable=False):
    """Extract the match from the similarity matrix."""
    match_groups = []
    for x in range(left_idx, right_idx):
        if row_col == 'row':
            matches = np.where(mm[x, :] > 0.5)[0].tolist()
        else:
            matches = np.where(mm[:, x] > 0.5)[0].tolist()
        matches = tuple(matches)
        if len(matches) != 1:
            match_groups.append(((x,), matches))
        else:
            if row_col == 'row':
                inverse_matches = np.where(mm[:, matches[0]] > 0.5)[0].tolist()
            else:
                inverse_matches = np.where(mm[matches[0], :] > 0.5)[0].tolist()
            inverse_matches = tuple(inverse_matches)
            match_groups.append((inverse_matches, matches))
    match_groups = list(set(match_groups))
    match_groups.sort(key=lambda x: x[0][0])
    if not readable:
        return match_groups
    else:
        match_groups_readable = []
        for mg in match_groups:
            match_groups_readable.append({
                "gt_idx": list(mg[0]),
                "trans_idx": list(mg[1])
            })
        return match_groups_readable


def get_match_matrix(sents1, sents2, verbose=False):
    """Get similarity alignment matrix between sents1 and sents2."""
    dots = find_similarity_matrix(sents1, sents2).cpu().numpy()

    if verbose:
        print(f"Dots computed, {dots.shape} shape")
    # use these scores for global alignment via needleman-wunsch
    m, n = dots.shape
    # penalty for doing a split or a merge
    penalty = -0.3

    # baseline to penalize matches below 0.4 SIM (almost never paraphrases)
    baseline = 0.0
    table = (dots - baseline) * np.ones((m, n))

    for i in tqdm.tqdm(range(0, m), desc="Table building...", disable=not verbose):
        for j in range(0, n):
            diagonal = 0 if i == 0 or j == 0 else table[i - 1, j - 1]
            top = 0 if i == 0 else table[i - 1, j]
            left = 0 if j == 0 else table[i, j - 1]
            top += penalty
            left += penalty
            table[i, j] += max(diagonal, top, left)

    # now backtrack to find alignment
    match_matrix = np.zeros((len(sents1), len(sents2)))

    best_bottom_val = np.max(table[-1]).item()
    best_right_val = np.max(table[:, -1]).item()

    if best_bottom_val >= best_right_val:
        i, j = m - 1, np.argmax(table[-1]).item()
    else:
        i, j = np.argmax(table[:, -1]).item(), n - 1

    while i > 0 and j > 0:
        score_prev = table[i, j] - (dots[i, j] - baseline)
        match_matrix[i, j] = 1

        if np.isclose(score_prev, table[i - 1, j - 1]):
            i -= 1
            j -= 1
        elif np.isclose(score_prev, table[i - 1, j] + penalty):
            i -= 1
        elif np.isclose(score_prev, table[i, j - 1] + penalty):
            j -= 1
        else:
            import pdb; pdb.set_trace()
            pass

    if i == 0 and j == 0:
        match_matrix[0, 0] = 1

    # finish tracing up to the top left cell if that's optimal
    elif i > 0:
        while True:
            match_matrix[i, 0] = 1
            score_prev = table[i, 0] - (dots[i, 0] - baseline)
            if i == 0:
                break
            if np.isclose(score_prev, table[i - 1, 0] + penalty):
                i -= 1
            else:
                break

    elif j > 0:
        while True:
            match_matrix[0, j] = 1
            score_prev = table[0, j] - (dots[0, j] - baseline)
            if j == 0:
                break
            if np.isclose(score_prev, table[0, j - 1] + penalty):
                j -= 1
            else:
                break

    idx0, idx1 = match_matrix.nonzero()
    # clean match matrix to remove 90 degree corners
    for i, j in zip(idx0, idx1):
        row_matches = match_matrix[i, :].nonzero()[0]
        col_matches = match_matrix[:, j].nonzero()[0]
        if len(row_matches) > 1 and len(col_matches) > 1:
            match_matrix[i, j] = 0

    return match_matrix, dots, table
