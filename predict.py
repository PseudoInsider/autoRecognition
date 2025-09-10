import torch
import pandas as pd
from transformers import RobertaTokenizerFast
from tqdm import tqdm
import torch.nn as nn
from transformers import RobertaModel
import re


class RoBERTaTokenClassifier(nn.Module):
    def __init__(self, model_name="roberta-large", num_labels=6):
        super().__init__()
        self.roberta = RobertaModel.from_pretrained(model_name)
        self.classifier = nn.Linear(self.roberta.config.hidden_size, num_labels)
        self.dropout = nn.Dropout(0.1)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state
        logits = self.classifier(self.dropout(sequence_output))
        if labels is not None:
            loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fn(logits.view(-1, logits.shape[-1]), labels.view(-1))
            return loss, logits
        return logits


class IOTagger:
    def __init__(self, model_path, num_labels=6, tokenizer_name="roberta-large"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = RoBERTaTokenClassifier(num_labels=num_labels).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        self.tokenizer = RobertaTokenizerFast.from_pretrained(tokenizer_name)
        self.label_to_id = {
            "O": 0, "I-source": 1, "I-residue": 2,
            "I-cue": 3, "I-content": 4, "I-hinge": 5
        }
        self.id2label = {v: k for k, v in self.label_to_id.items()}
        self.label_mapping = {
            "I-source": "source", "I-cue": "cue", "I-hinge": "hinge",
            "I-residue": "residue", "I-content": "content", "O": "O"
        }

    def process_token_results(self, token_results):
        """Process token-level predictions into tagged sentences and categorized text."""
        words = [token['word'] for token in token_results if token['word'].strip()]
        pred_labels = [token['pred_label'] for token in token_results if token['word'].strip()]

        special_tokens = {"<s>", "</s>", ""}
        processed_words = [word for word in words if word not in special_tokens]
        filtered_labels = [label for word, label in zip(words, pred_labels) if word not in special_tokens]

        # Reconstruct clean sentence
        clean_sentence_parts = []
        i = 0
        while i < len(processed_words):
            token = processed_words[i]
            if token.startswith("##"):
                clean_sentence_parts[-1] += token[2:]
            else:
                if clean_sentence_parts:
                    clean_sentence_parts.append(" ")
                clean_sentence_parts.append(token)
            i += 1
        clean_sentence = "".join(clean_sentence_parts)

        # Map IO labels to categories
        categories = [self.label_mapping.get(label, "O") for label in filtered_labels]

        # Build tagged sentence
        tagged_sentence_parts = []
        current_label = None
        for word, category in zip(processed_words, categories):
            if category == "O":
                if current_label is not None:
                    tagged_sentence_parts.append(f"</{current_label}>")
                    current_label = None
                if word.startswith("##"):
                    tagged_sentence_parts[-1] += word[2:]
                else:
                    if tagged_sentence_parts:
                        tagged_sentence_parts.append(" ")
                    tagged_sentence_parts.append(word)
            else:
                if category != current_label:
                    if current_label is not None:
                        tagged_sentence_parts.append(f"</{current_label}>")
                    tagged_sentence_parts.append(f"<{category}>")
                    current_label = category
                if word.startswith("##"):
                    tagged_sentence_parts[-1] += word[2:]
                else:
                    if tagged_sentence_parts and not tagged_sentence_parts[-1].endswith(">"):
                        tagged_sentence_parts.append(" ")
                    tagged_sentence_parts.append(word)
        if current_label is not None:
            tagged_sentence_parts.append(f"</{current_label}>")

        tagged_sentence = "".join(tagged_sentence_parts)

        row = {
            "ReportingSentence": clean_sentence,
            "tagged_sentences": tagged_sentence,
            "cue": self.extract_labeled_text(tagged_sentence, "cue"),
            "source": self.extract_labeled_text(tagged_sentence, "source"),
            "content": self.extract_labeled_text(tagged_sentence, "content"),
            "hinge": self.extract_labeled_text(tagged_sentence, "hinge"),
            "residue": self.extract_labeled_text(tagged_sentence, "residue"),
        }
        return row

    def extract_labeled_text(self, tagged_sentence, tag):
        """Extract content marked by a specific tag and join disjoint parts with '///'."""
        matches = re.findall(fr"<{tag}>(.*?)(?=(</{tag}>|$))", tagged_sentence)
        return "///".join(match[0].strip() for match in matches) if matches else "N/A"

    def predict_dataset(self, input_csv, output_csv="predicted_result.csv"):
        df = pd.read_csv(input_csv)
        results = []
        print('Predicting labels for the dataset...')

        for index, row in tqdm(df.iterrows(), total=len(df)):
            no = row.get("No.", index)
            text_id = row.get("TextID", f"row-{index}")
            context = str(row.get("Context", ""))
            reporting_sentence = str(row.get("ReportingSentence", ""))

            # Tokenization with truncation to avoid >512 errors
            inputs = self.tokenizer(
                reporting_sentence,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                logits = self.model(inputs['input_ids'], attention_mask=inputs['attention_mask'])
                probabilities = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()
                predictions = logits.argmax(dim=-1)[0].cpu().numpy()

            # Get offsets (also truncated to 512)
            inputs_with_offsets = self.tokenizer(
                reporting_sentence,
                return_offsets_mapping=True,
                truncation=True,
                max_length=512
            )
            offsets = inputs_with_offsets["offset_mapping"]

            token_results = []
            for idx in range(len(predictions)):
                if idx >= len(offsets):
                    break
                start, end = offsets[idx]
                word = reporting_sentence[start:end]
                pred_label = self.id2label.get(predictions[idx], "N/A")
                token_results.append({
                    "word": word,
                    "pred_label": pred_label,
                    "probability": max(probabilities[idx]),
                    "probabilities": probabilities[idx].tolist(),
                })

            processed_row = self.process_token_results(token_results)

            final_row = {
                "No.": no,
                "TextID": text_id,
                "Context": context,
                "ReportingSentence": reporting_sentence,
                "tagged_sentences": processed_row["tagged_sentences"],
                "cue": processed_row["cue"],
                "source": processed_row["source"],
                "content": processed_row["content"],
                "hinge": processed_row["hinge"],
                "residue": processed_row["residue"],
            }
            results.append(final_row)

        df_out = pd.DataFrame(results)
        df_out.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"Prediction results saved to '{output_csv}'.")
        return results


if __name__ == "__main__":
    tagger = IOTagger(model_path='V1-model.bin')
    results = tagger.predict_dataset(
        input_csv='cc_input_2025.csv',
        output_csv='predicted_result.csv'
    )
    print("Prediction completed.")
