import pickle
import random

with open("par3.pkl", "rb") as f:
    data = pickle.load(f)

# change this or select from data.keys()
book_key = "anna_karenina_ru"

# getting source data for a given book
source_paras = data[book_key]["source_paras"]

# getting google translate data for a given book
gt_paras = data[book_key]["gt_paras"]

# getting human translator data for a given book
translator_data = data[book_key]["translator_data"]
num_trans = len(translator_data) # number of human translations

# printing out one random paragraph alignment from Anna Karenina
print("PARAGRAPH-LEVEL ALIGNMENTS")
para_idx = random.randint(0, len(data[book_key]["source_paras"]))
print("Source text: ", source_paras[para_idx], "\n")
print("Google Translate text: ", gt_paras[para_idx], "\n")
for i in range(num_trans):
    print(f"Translator {str(i+1)} text: ", translator_data[f"translator_{i+1}"]["translator_paras"][para_idx], "\n")
print("\n\n")

# print first sentence alignment from the paragraph above
# printing out one random paragraph alignment from Anna Karenina
print("SENTENCE-LEVEL ALIGNMENTS")
for i in range(num_trans):
    print(f"Translator {str(i+1)}: ")
    trans_sents = translator_data[f"translator_{i+1}"]["sent_alignments"][para_idx][0]["trans"]
    for sent in trans_sents: # could be more than one sentence if the translator split or merged sentences in the source text
        print(sent, "\n")
    print(f"Google Translate: ")
    gt_sents = translator_data[f"translator_{i+1}"]["sent_alignments"][para_idx][0]["gt"]
    for sent in gt_sents: # could be more than one sentence if the translator split or merged sentences in the source text
        print(sent, "\n")
    print("-------------------------------")
