# Par3

## Introduction
Par3 is a dataset comprised of aligned paragraphs of public-domain foreign language novels and their human-written English translations. The alignments between source text and English translations were found by passing the source text through Google Translate and aligning the output with the English translations. Alignments were found using the Needleman-Wunsch algorithm with cosine similarity as the scoring function. The data for each source novel contains at least 2 (and up to 5) human-written translations, and we provide the intermediate Google Translate output used to align source text and human translations. Additionally, the dataset contains sentence-level alignments between the human translations and the Google Translate translations. No more than 50% of the paragraphs in any human translation are present in Par3, and the original order of the paragraphs has been shuffled.

## Corpus Statistics
|    | # |
| ------------- | ------------- |
| Books  | 106 |
| Source languages | 16 |
| Aligned paragraphs| 122,819 |
| Aligned sentences| 1,581,988* |
| Avg sentences/paragraph | 5.6 |
| Avg tokens/sentence | 18.8 |

*This is an estimate based on the number of pairs we have between Google Translate sentence and human-written sentences.

## Dataset Examples

### Paragraph-level Alignments
Source paragraph:  
>Cependant le vaisseau français et l'espagnol continuèrent leur route, et Candide continua ses conversations avec Martin. Ils disputèrent quinze jours de suite, et au bout de quinze jours ils étaient aussi avancés que le premier. Mais enfin ils parlaient, ils se communiquaient des idées, ils se consolaient. Candide caressait son mouton. « Puisque je t'ai retrouvé, dit-il, je pourrai bien retrouver Cunégonde. »

Google Translate paragraph:
>However, the French vessel and the Spanish continued their journey, and Candide continued his conversations with Martin. They disputed fifteen days in succession, and at the end of fifteen days they were as advanced as the first. But in the end they talked, they communicated ideas, they consoled each other. Candide stroked his sheep. "Since I have found you," he said, "I could very well find Cunegonde." »

Translator 1 paragraph:  
>The French and Spanish ships continued on their journey, and Candide and Martin continued their conversation. They disputed for fifteen days in a row and at the end of that time they were just as far advanced as the first moment they began. However, they had the satisfaction of talking, of communicating their ideas, and of comforting each other. Candide embraced his sheep: "Since I have found you again," said he, "I may possibly find my Cunégonde once more."

Translator 2 paragraph:
> Meanwhile the French and Spanish vessels continued on their journey, and Candide continued his talks with Martin. They disputed for fifteen days in a row, and at the end of that time were just as much in agreement as at the beginning. But at least they were talking, they exchanged ideas, they consoled one another. Candide caressed his sheep. —Since I have found you again, said he, I may well rediscover Miss Cunégonde.

### Sentence-level Alignments
Given a Google Translate paragraph g and aligned human translator paragraphs t<sub>1</sub>,..., t<sub>n</sub>, we compute sentence-level alignments between g and t<sub>1</sub>, g and t<sub>2</sub>,..., and g and t<sub>n</sub> separately. This is because unlike Google Translate, human translators often split or merge sentences, which means that it isn't always possible to align all sentences from a given translator to all sentences of the GT. Thus, we cannot provide n-way alignments for sentences in the same way that we did for paragraphs.

## Code

### Setup

```
git clone https://github.com/ngram-lab/par3
cd par3
python3.7 -m virtualenv par3-venv
source par3-venv/bin/activate
pip install .
python -m spacy download en_core_web_sm
```

### Running alignment code

```
python -m par3_align.align_books --dataset par3_dataset_test --verbose --ouput_file aligned2.pkl
diff par3_dataset_test/candide_fr/aligned.pkl par3_dataset_test/candide_fr/aligned2.pkl
```

The dataset folder should look something like this for successful alignment,

```
par3_dataset_test/candide_fr
├── src_txts
│   └── candide_src.txt
└── trans_txts
    ├── candide_gt.txt
    ├── candide_henry_morley.txt
    └── candide_robert_adams.txt
```

In this case, the output will be in `dataset_test/candide_fr/align.pkl`. You can visualize the alignment in `html/candide_fr.html` if you pass the flag `--output_html html`. Note that you need `gawk` installed for this to work.

## Dataset Details
The dataset is pickled dictionary in `par3.pkl`.

### Accessing Paragraph Alignments

We provide the script `sample_par3.py` to demonstrate how to access paragraph and sentence alignments in Par3.

https://github.com/ngram-lab/par3/blob/bb42d319c6e313383a1594e8e3367811c3efa2ea/sample_par3.py#L8 specifies a book from which to randomly sample a paragraph.
https://github.com/ngram-lab/par3/blob/bb42d319c6e313383a1594e8e3367811c3efa2ea/sample_par3.py#L11 stores all source paragraphs for that book in the variable `source_paras`.
https://github.com/ngram-lab/par3/blob/bb42d319c6e313383a1594e8e3367811c3efa2ea/sample_par3.py#L14 stores all Google Translate paragraphs for that book in the variable `gt_paras`.
https://github.com/ngram-lab/par3/blob/bb42d319c6e313383a1594e8e3367811c3efa2ea/sample_par3.py#L17 stores all translator data for that book in the variable `translator_data`.
`translator_data` is a dictionary containing data for each human translation of the source text. Each translation's data can be accessed with the key `translator_i`, where `i` is the number of the translation.
https://github.com/ngram-lab/par3/blob/bb42d319c6e313383a1594e8e3367811c3efa2ea/sample_par3.py#L24-L25 demonstrates how to access the paragraphs for each human translation that correspond to `source_paras` and `gt_paras`.

### Accessing Sentence Alignments
Note that in the following line
https://github.com/ngram-lab/par3/blob/0fe6e037262fc3097e3214e672de5352c603acfe/sample_par3.py#L32
we iterate over each human translator's data because sentence-level alignments are independent for each Google Translate-human translation pair.

https://github.com/ngram-lab/par3/blob/0fe6e037262fc3097e3214e672de5352c603acfe/sample_par3.py#L34 usually stores a singleton list of the first sentence by `translator_i` in the randomly sampled paragraph from above. However, it's possible that this list contains more than one sentence.
https://github.com/ngram-lab/par3/blob/0fe6e037262fc3097e3214e672de5352c603acfe/sample_par3.py#L35-L36

Similarly, we access the corresponding Google Translation sentence(s) for `translation_i`:
https://github.com/ngram-lab/par3/blob/0fe6e037262fc3097e3214e672de5352c603acfe/sample_par3.py#L38-L40

### Dataset Structure  
```
{
   "book_title": {
      "source_paras": [source_para_1,source_para2],
      "gt_paras": [gt_para_1, gt_para2],
      "translator_data": {
          "translator_1": {
              "translator_paras": [trans_para_1, trans_para_2],
              "sent_alignments": [
                  [
                    {"gt": [[gt_para_1_sent_1]],
                    "trans": [[trans_para_1_sent_1]]},
                    {"gt": [[gt_para_1_sent_2]],
                    "trans": [[trans_para_1_sent_2]]},
                  ],
                  [
                    {"gt": [[gt_para_2_sent_1]],
                    "trans": [[trans_para_2_sent_1a, trans_para_2_sent_1b]},
                  ],
              ]
          }
      }

}
```

`data.keys()` is a list of foreign language novel titles with two-character source language codes appended to them. For example `data["don_quixote_es"]` contains the data corresponding to *Don Quixote*, a Spanish novel.

`data[title_langcode]` is a dictionary with 3 keys:
1. `"source_paras"`
2. `"gt_paras"`
3. `"translator_data"`

`data[title_langcode]["source_paras"]` is a list of paragraphs in the source language. `data[title_langcode]["gt_paras"]` is a list of the *same length* as `data[title_langcode]["source_paras"]` that contains the corresponding paragraph from Google Translate. Therefore, `data[title_langcode]["source_paras][x]"` is aligned with `"data[title_langcode][gt_paras][x]"`.

`data[title_langcode]["translator_data"]` is a dictionary with `n` keys in the format `translator_i`, where `n` is between 2 and 5 and represents the number of different English translations included for a specific source text.

`data[title_langcode]["translator_data"][translator_i]` is a dictionary with 2 keys:
1. `"translator_paras"`
2. `"sent_alignments"`

`data[title_langcode]["translator_data"][translator_i]["translator_paras"]` is analogous to `data[title_langcode]["source_paras"]` and `data[title_langcode]["gt_paras"]`. It is a list of the same length as `data[title_langcode]["source_paras"]` For any index `x`, `data[title_langcode]["translator_data"][translator_i]["translator_paras"][x]` is aligned with `data[title_langcode]["source_paras"][x]` and `data[title_langcode]["gt_paras"][x]`.

`data[title_langcode]["translator_data"][translator_i]["sent_alignments"]` is a list of lists the same length as `data[title_langcode]["source_paras"]`. Each list corresponds to one paragraph and contains a list of dictionaries. The number of dictionaries is equal to the number of sentences in that paragraph. The `"gt"` key is a list of the Google Translate sentence(s), while the `"trans"` key is a list of the corresponding transltor sentence(s). Note that these two lists need not be the same length in the case that sentences within a paragraph were split or merged by different translators.

### Citation Information
If you use this dataset, please cite it as follows:
```
@misc{Par3_2022,
author = {Marzena Karpinska and Katherine Thai and Kalpesh Krishna and John Wieting and Moira Inghilleri and Mohit Iyyer},
month = {5},
title = {{Par3}},
url = {https://github.com/ngram-lab/par3},
year = {2022}
}
```
