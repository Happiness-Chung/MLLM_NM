from tqdm import tqdm
from collections import Counter

def simple_tokenize(text):
    return text.split()

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content.strip().split('\n\n')

def skip_bigrams(sequence, k=2):
    skip_bigrams_list = []
    n = len(sequence)
    for i in range(n):
        for j in range(i + 1, min(i + k + 1, n)):
            skip_bigrams_list.append((sequence[i], sequence[j]))
    return skip_bigrams_list

def rouge_s(generated_tokens, reference_tokens, k=2):

    generated_skip_bigrams = skip_bigrams(generated_tokens, k)
    reference_skip_bigrams = skip_bigrams(reference_tokens, k)

    generated_counter = Counter(generated_skip_bigrams)
    reference_counter = Counter(reference_skip_bigrams)

    overlap = sum((generated_counter & reference_counter).values())

    if len(generated_skip_bigrams) == 0 or len(reference_skip_bigrams) == 0:
        return 0.0

    precision = overlap / len(generated_skip_bigrams)
    recall = overlap / len(reference_skip_bigrams)

    if precision + recall == 0:
        return 0.0

    f1_score = 2 * (precision * recall) / (precision + recall)
    return f1_score

generated_file = '/root/MLLM/LLaVA-NeXT/results/preds.txt'
label_file = '/root/MLLM/LLaVA-NeXT/results/labels.txt'

generated_texts = read_file(generated_file)
reference_texts = read_file(label_file)

rouge_scores = []

for generated, reference in tqdm(zip(generated_texts, reference_texts), total=len(generated_texts)):

    # Tokenize the texts
    generated_tokens = simple_tokenize(generated)
    reference_tokens = simple_tokenize(reference)

    rouge = rouge_s(generated_tokens, reference_tokens)
    rouge_scores.append(rouge)

rouge_s_scores = sum(rouge_scores) / len(rouge_scores)

print(f"ROUGE-S: {rouge_s_scores:.4f}")
