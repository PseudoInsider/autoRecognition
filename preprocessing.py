import os
import pandas as pd
import spacy
import logging
import re
from spacy.tokens import Token

# __order__ = 7
class PreprocessText:
    def __init__(self, config):
        self.config = config
        self.nlp = spacy.load("en_core_web_sm")
        self.context_range = config.get("context_range", 50)
        self.max_merge = config.get("max_merge", 3)
        self.reporting_verbs_file = config["reporting_verbs_file"]
        self.output_path = os.path.join(os.path.dirname(__file__), config["output_directory"], "output.csv")
        self.input_path = os.path.join(os.path.dirname(__file__), config["input_directory"])

        # Create separate pipeline for sentence splitting
        self.sentencizer_nlp = spacy.blank("en")
        self.sentencizer_nlp.add_pipe("sentencizer")

        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Add extension for tracking original sentence text
        if not Token.has_extension("original_text"):
            Token.set_extension("original_text", default=None)

    def clean_text(self, text):
        """Clean text while preserving linguistic structure"""
        # Normalize quotes and whitespace
        text = re.sub(r'[“”]', '"', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def read_file(self, input_path):
        """Reads and processes text files with proper text cleaning"""
        all_sentences = []

        for file_name in os.listdir(input_path):
            if file_name.endswith('.txt'):
                file_path = os.path.join(input_path, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = self.clean_text(f.read())

                    basic_sents = self.cut_sentences(text)
                    final_sents = self.check_sentences(basic_sents)

                    # Apply text normalization per sentence
                    processed_sents = []
                    for sent in final_sents:
                        # Preserve original spacing around punctuation
                        sent = re.sub(r'\s+([.,!?])', r'\1', sent)
                        sent = re.sub(r'([.,])(\w)', r'\1 \2', sent)
                        processed_sents.append(sent)

                    all_sentences.extend([(file_name, sent) for sent in processed_sents])

                except Exception as e:
                    logging.error(f"Error reading file {file_name}: {e}")
                    continue

        return all_sentences

    def cut_sentences(self, text):
        """Split text into sentences using custom sentencizer"""
        doc = self.sentencizer_nlp(text)
        return [sent.text.strip() for sent in doc.sents]

    def check_sentences(self, basic_sents):
        """Merge sentences with quote handling using state machine"""
        final_sents = []
        i = 0
        n = len(basic_sents)

        while i < n:
            current_sent = basic_sents[i]
            merged = [current_sent]
            quote_count = current_sent.count('"')
            merge_count = 0

            # Track quote state machine
            in_quote = quote_count % 2 != 0

            while in_quote and merge_count < self.max_merge and (i + 1) < n:
                i += 1
                merge_count += 1
                next_sent = basic_sents[i]
                merged.append(next_sent)
                quote_count += next_sent.count('"')
                in_quote = quote_count % 2 != 0

            final_sents.append(" ".join(merged))
            i += 1

        return final_sents

    def validate_reporting_verbs(self, doc, reporting_verbs):
        """Enhanced reporting verb detection with comprehensive validation"""
        verbs = []

        for token in doc:
            # Basic verb validation
            if token.pos_ in {"VERB", "AUX"} and token.lemma_.lower() in reporting_verbs:
                # Check for subject dependencies
                has_subject = any(child.dep_ in {"nsubj", "nsubjpass"} for child in token.children)

                # Check for object dependencies
                has_object = any(
                    child.dep_ in {"dobj", "iobj", "pobj", "attr", "oprd"}
                    for child in token.children
                )

                # Check for clausal complements
                has_clause = any(
                    child.dep_ in {"ccomp", "xcomp", "acl", "advcl", "relcl"}
                    for child in token.children
                )

                # Check for prepositional complements
                has_prep = any(
                    child.dep_ == "prep" and any(
                        grandchild.dep_ in {"pobj", "pcomp"}
                        for grandchild in child.children
                    )
                    for child in token.children
                )

                # Check for reporting patterns
                has_reporting_pattern = (
                        has_subject or  # Subject + verb
                        has_object or  # Verb + object
                        has_clause or  # Verb + clause
                        has_prep  # Verb + prepositional phrase
                )

                # Additional validation for direct speech
                has_direct_speech = any(
                    child.text in {'"', '“', '”'} or child.is_quote
                    for child in token.subtree
                )

                # If any valid pattern is found
                if has_reporting_pattern or has_direct_speech:
                    verbs.append(token)

        return verbs

    def preprocess_text(self):
        """Main processing with linguistic validation"""
        if not os.path.exists(self.input_path):
            logging.error(f"Input path {self.input_path} does not exist.")
            return

        try:
            # Load reporting verbs with validation
            with open(self.reporting_verbs_file, 'r', encoding='utf-8') as f:
                reporting_verbs = {line.strip().lower() for line in f if line.strip()}

            all_sentences = self.read_file(self.input_path)
            if not all_sentences:
                logging.warning("No sentences extracted from input files.")
                return

            all_rows = []
            for idx, (file_name, sentence) in enumerate(all_sentences):
                # Process with original text preservation
                doc = self.nlp(sentence)
                for token in doc:
                    token._.original_text = token.text

                # Validate reporting verbs linguistically
                verbs = self.validate_reporting_verbs(doc, reporting_verbs)
                if not verbs:
                    continue

                # Build modified sentence with annotations
                modified = []
                for token in doc:
                    if token in verbs:
                        modified.append(f"{token.text}")
                    else:
                        modified.append(token.text)

                # Get context with original sentences
                start = max(0, idx - self.context_range)
                end = min(len(all_sentences), idx + self.context_range + 1)
                context = " ".join([s for _, s in all_sentences[start:end]])

                all_rows.append([
                    len(all_rows) + 1,
                    file_name,
                    context.strip(),
                    " ".join(modified).replace(" n't", "n't")  # Fix contractions
                ])

            if all_rows:
                os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
                df = pd.DataFrame(all_rows, columns=["No.", "TextID", "Context", "ReportingSentence"])
                df.to_csv(self.output_path, index=False)
                logging.info(f"Saved results to {self.output_path}")
            else:
                logging.warning("No reporting sentences found.")

        except Exception as e:
            logging.exception(f"Critical error in preprocessing: {e}")


def main():
    config = {
        'context_range': 3,
        'max_merge': 3,
        'reporting_verbs_file': 'reporting_verbs.csv',
        'output_directory': 'output',
        'input_directory': 'test',
    }

    preprocessor = PreprocessText(config)
    preprocessor.preprocess_text()


if __name__ == "__main__":
    main()
