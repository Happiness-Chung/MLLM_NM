from tqdm import tqdm
import nltk
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from sklearn.metrics import accuracy_score

nltk.download('punkt', download_dir='/root/MLLM/LLaVA-NeXT')

# 다운로드 후에 로컬 경로를 추가
nltk.data.path.append('/root/MLLM/LLaVA-NeXT')

def simple_tokenize(text):
    return text.split()

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content.strip().split('\n\n')

def compute_scores(generated_texts, reference_texts):
    bleu_scores = []
    rouge_1_f1_scores = []
    rouge_2_f1_scores = []
    rouge_l_f1_scores = []
    rouge_s_f1_scores = []

    rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    for generated, reference in tqdm(zip(generated_texts, reference_texts), total=len(generated_texts)):
        # Tokenize the texts
        generated_tokens = simple_tokenize(generated)
        reference_tokens = [simple_tokenize(reference)]

        # Compute BLEU score
        bleu_score = sentence_bleu(reference_tokens, generated_tokens)
        bleu_scores.append(bleu_score)

        # Compute ROUGE-L F1 score
        rouge_scores = rouge.score(reference, generated)
        rouge_1_f1_scores.append(rouge_scores['rouge1'].fmeasure)
        rouge_2_f1_scores.append(rouge_scores['rouge2'].fmeasure)
        rouge_l_f1_scores.append(rouge_scores['rougeL'].fmeasure)

       

    return {
        "BLEU": sum(bleu_scores) / len(bleu_scores),
        "ROUGE-1": sum(rouge_1_f1_scores) / len(rouge_1_f1_scores),
        "ROUGE-2": sum(rouge_2_f1_scores) / len(rouge_2_f1_scores),
        "ROUGE-L": sum(rouge_l_f1_scores) / len(rouge_l_f1_scores),
    }

# Example usage
generated_file = '/root/MLLM/LLaVA-NeXT/results/preds.txt'
label_file = '/root/MLLM/LLaVA-NeXT/results/labels.txt'

# Read files
generated_texts = read_file(generated_file)
reference_texts = read_file(label_file)

# Compute scores
scores = compute_scores(generated_texts, reference_texts)
print(f"BLEU: {scores['BLEU']:.4f}")
print(f"ROUGE-1: {scores['ROUGE-1']:.4f}")
print(f"ROUGE-2: {scores['ROUGE-2']:.4f}")
print(f"ROUGE-L: {scores['ROUGE-L']:.4f}")
print(f"BLEU: {scores['BLEU']:.4f}, ROUGE-L: {scores['ROUGE-L']:.4f}")
