import os
import re
import spacy
from collections import Counter, defaultdict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Load English NLP model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")
# Define keyword dictionary with weights
CHINA_KEYWORDS = {
    "china": 4, "beijing": 3, "chinese": 3, "xi jinping": 3,
    "belt and road": 4, "cpc": 2, "taiwan": 2, "macao": 3,
    "prc": 2, "pla": 3, "bri": 3, "hong kong": 3,
    "tibet": 3, "wuhan": 2, "hangzhou": 3, "deepseek": 2, "panda": 1,
    "shanghai": 3, "shenzhen": 3, "guangzhou": 3, "tiananmen": 3,
    "huawei": 3, "tiktok": 3, "alibaba": 3, "jd.com": 2,
    "one china policy": 4, "south china sea": 4, "censorship": 2,
    "great firewall": 3, "xi’s policies": 3, "economic corridor": 2,
    "chinese military": 3, "made in china 2025": 3, "chip war": 3,
    "evergrande": 2, "property crisis": 2, "real estate bubble": 2,
}
# Contextual phrases that indicate relation to China
CHINA_PHRASES = [
    "chinese foreign policy", "chinese government",
    "chinese investment", "beijing's response",
    "xi jinping's leadership", "china-us relations",
    "china's economic growth", "china's military expansion",
    "chinese trade policies", "belt and road initiative",
    "taiwan strait tensions", "hong kong protests",
    "tibet autonomy", "xinjiang policies",
    "china's tech industry", "chinese surveillance",
    "beijing's stance", "china's influence in africa",
    "chinese soft power", "chinese digital currency",
    "china's global ambitions", "shanghai stock exchange",
    "china's zero-covid policy", "chinese semiconductor industry",
]


def extract_china_features(text):
    """Extract multiple features related to China from text"""
    text_lower = text.lower()
    features = {}

    # Feature 1: Keyword Frequency Score
    features['keyword_score'] = sum(text_lower.count(word) * weight for word, weight in CHINA_KEYWORDS.items())

    # Feature 2: Exact Keyword Count
    word_counts = Counter(re.findall(r'\b\w+\b', text_lower))
    features['china_mentions'] = sum(word_counts.get(word, 0) for word in CHINA_KEYWORDS.keys())

    # Feature 3: Named Entity Recognition (NER)
    doc = nlp(text)
    features['china_entities'] = sum(1 for ent in doc.ents if ent.label_ in ["GPE", "NORP"] and any(
        china_word in ent.text.lower() for china_word in CHINA_KEYWORDS.keys()))

    # Feature 4: Contextual Phrase Matching
    features['phrase_score'] = sum(1 for phrase in CHINA_PHRASES if phrase in text_lower)

    return features


def cluster_documents(texts, filenames, n_clusters=3):
    """Cluster documents using K-Means based on TF-IDF features"""
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(texts)

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # Reduce dimensionality for visualization
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(X.toarray())

    return clusters, reduced_features


def visualize_clusters(reduced_features, clusters, filenames, results):
    """Enhanced visualization showing both clusters and relation status"""
    plt.figure(figsize=(14, 10))

    # Create mapping of filename to relation status
    relation_status = {filename: 'Related' if any(filename == r[0] for r in results['related'])
    else 'Not Related' for filename in filenames}

    # Define visual properties
    cluster_markers = ['o', 's', 'D', '^', 'v']  # Different markers for clusters
    color_map = {'Related': 'red', 'Not Related': 'blue'}

    # Plot each point with appropriate style
    for i, (x, y) in enumerate(reduced_features):
        cluster = clusters[i]
        status = relation_status[filenames[i]]

        plt.scatter(x, y,
                    c=color_map[status],
                    marker=cluster_markers[cluster % len(cluster_markers)],
                    s=100,  # Size of points
                    alpha=0.7,
                    edgecolors='w',
                    linewidths=0.5)

    # Create custom legends
    from matplotlib.lines import Line2D

    # Legend for relation status
    relation_legend = [Line2D([0], [0], marker='o', color='w', label='Related',
                              markerfacecolor='red', markersize=10),
                       Line2D([0], [0], marker='o', color='w', label='Not Related',
                              markerfacecolor='blue', markersize=10)]

    # Legend for clusters
    cluster_legend = [Line2D([0], [0], marker=cluster_markers[i], color='w', label=f'Cluster {i}',
                             markerfacecolor='gray', markersize=10)
                      for i in range(max(clusters) + 1)]

    # Add legends to plot
    first_legend = plt.legend(handles=relation_legend, title='Relation to China',
                              loc='upper right', bbox_to_anchor=(1, 1))
    plt.gca().add_artist(first_legend)
    plt.legend(handles=cluster_legend, title='Clusters',
               loc='upper right', bbox_to_anchor=(1, 0.85))

    # Add some annotations for important points
    for i, (x, y) in enumerate(reduced_features[:15]):  # Label first 15 points
        plt.annotate(f"{filenames[i]}", (x, y),
                     textcoords="offset points",
                     xytext=(0, 5), ha='center', fontsize=8)

    # Add title and labels
    plt.title("Document Clustering with China Relation Status", pad=20)
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.grid(True, alpha=0.3)

    # Add statistics to plot
    stats_text = (f"Total documents: {len(filenames)}\n"
                  f"Related to China: {len(results['related'])}\n"
                  f"Clusters: {max(clusters) + 1}")
    plt.text(0.02, 0.98, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', alpha=0.2))

    plt.tight_layout()
    plt.show()


def calculate_cluster_weights(clusters, decay_rate=0.7, min_weight=0.1):
    """
    Calculate cluster weights using exponential decay
    :param clusters: List of cluster assignments
    :param decay_rate: Rate of decay (0-1, smaller means faster decay)
    :param min_weight: Minimum weight for any cluster
    :return: Dictionary of {cluster_id: weight}
    """
    cluster_counts = Counter(clusters)
    sorted_clusters = sorted(cluster_counts.items(), key=lambda x: -x[1])  # Sort by size descending

    weights = {}
    for rank, (cluster, _) in enumerate(sorted_clusters):
        weights[cluster] = max(min_weight, decay_rate ** rank)  # Exponential decay formula

    # Normalize to sum to 1
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def is_related_to_china(text, features=None, cluster_weights=None):
    """Determine if text is related to China with cluster weighting"""
    if features is None:
        features = extract_china_features(text)

    # Normalize features
    keyword_score = min(features['keyword_score'] / 10, 1.0)
    phrase_score = min(features['phrase_score'] / 2, 1.0)
    entity_score = min(features['china_entities'] / 3, 1.0)

    # Base score (weighted sum)
    base_score = 0.4 * keyword_score + 0.2 * phrase_score + 0.3 * entity_score

    # Combine with cluster weight if available
    combined_score = base_score
    if 'cluster' in features and cluster_weights:
        cluster = features['cluster']
        cluster_weight = 0.1  # Cluster contributes 10% to final score
        cluster_factor = cluster_weights.get(cluster, 0.2)
        combined_score = (1 - cluster_weight) * base_score + cluster_weight * cluster_factor

    threshold = 0.5
    return combined_score >= threshold, {
        'score': combined_score,
        'base_score': base_score,
        'keyword_score': keyword_score,
        'phrase_score': phrase_score,
        'entity_score': entity_score,
        'cluster': features.get('cluster'),
        'cluster_weight': cluster_weights.get(features.get('cluster')) if cluster_weights else None
    }


def analyze_texts_in_directory(directory_path, n_clusters=3):
    """Analyze all text files in a directory for China relation with clustering visualization.

    Args:
        directory_path: Path to directory containing text files
        n_clusters: Number of clusters to use (default=3)

    Returns:
        Dictionary containing:
        - related: List of (filename, details) tuples for China-related files
        - not_related: List of (filename, details) tuples for non-related files
        - clusters: List of (filename, cluster_id) tuples
        - reduced_features: 2D PCA coordinates for visualization
        - cluster_stats: Statistics about each cluster
    """
    results = {
        'related': [],
        'not_related': [],
        'error': [],
        'clusters': [],
        'reduced_features': None,
        'cluster_stats': defaultdict(lambda: {'related': 0, 'total': 0})
    }

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist")

    # Get all text files
    txt_files = [f for f in os.listdir(directory_path)
                 if f.lower().endswith('.txt') and os.path.isfile(os.path.join(directory_path, f))]

    if not txt_files:
        return results

    texts = []
    filenames = []
    features_list = []

    # Process each file
    for file_name in txt_files:
        file_path = os.path.join(directory_path, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                features = extract_china_features(content)

                texts.append(content)
                filenames.append(file_name)
                features_list.append(features)

        except Exception as e:
            results['error'].append(f"{file_name} - {str(e)}")

    # Only proceed if we have texts to analyze
    if texts:
        # Adjust cluster count if needed
        n_clusters = min(n_clusters, max(2, len(texts) // 3))

        # Cluster documents
        clusters, reduced_features = cluster_documents(texts, filenames, n_clusters=n_clusters)
        results['reduced_features'] = reduced_features
        results['clusters'] = list(zip(filenames, clusters))

        # Calculate cluster weights using exponential decay
        cluster_weights = calculate_cluster_weights(clusters, decay_rate=0.6)

        # Classify documents
        for filename, text, features, cluster in zip(filenames, texts, features_list, clusters):
            features['cluster'] = cluster
            related, details = is_related_to_china(
                text,
                features=features,
                cluster_weights=cluster_weights
            )

            # Store results
            if related:
                results['related'].append((filename, details))
                results['cluster_stats'][cluster]['related'] += 1
            else:
                results['not_related'].append((filename, details))

            results['cluster_stats'][cluster]['total'] += 1

    return results


def cluster_documents(texts, filenames, n_clusters=3):
    """Cluster documents and return cluster assignments and reduced features"""
    # Vectorize texts
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(texts)

    # Cluster using KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # Reduce dimensionality for visualization
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(X.toarray())

    return clusters, reduced_features


def calculate_cluster_weights(clusters, decay_rate=0.7, min_weight=0.1):
    """Calculate weights for clusters using exponential decay"""
    cluster_counts = Counter(clusters)
    if not cluster_counts:
        return {}

    # Sort clusters by size (descending)
    sorted_clusters = sorted(cluster_counts.items(), key=lambda x: -x[1])

    # Apply exponential decay
    weights = {
        cluster: max(min_weight, decay_rate ** rank)
        for rank, (cluster, _) in enumerate(sorted_clusters)
    }

    # Normalize weights to sum to 1
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def print_results(results):
    """Print the analysis results in a readable format."""
    if not results:
        print("No results or an error occurred.")
        return

    print("\n=== Results ===")
    print(f"Related to China ({len(results['related'])} files):")
    for filename, details in results['related']:
        print(f" - {filename}")
        print(f"   Score: {details['score']:.2f} (Base: {details['base_score']:.2f})")
        print(f"   Cluster: {details.get('cluster', 'N/A')}")
        print(
            f"   Features: Keywords={details['keyword_score']:.2f}, Phrases={details['phrase_score']:.2f}, Entities={details['entity_score']:.2f}")

    print(f"\nNot related to China ({len(results['not_related'])} files):")
    for filename, details in results['not_related']:
        print(f" - {filename} | Cluster: {details.get('cluster', 'N/A')} | Score: {details['score']:.2f}")

    if results['error']:
        print(f"\nFiles with errors ({len(results['error'])}):")
        for error in results['error']:
            print(f" - {error}")

    if 'clusters' in results:
        print("\n=== Cluster Distribution ===")
        cluster_counts = Counter(cluster for _, cluster in results['clusters'])
        for cluster, count in sorted(cluster_counts.items()):
            print(f"Cluster {cluster}: {count} documents")

        # Calculate relation percentage per cluster
        print("\n=== Relation by Cluster ===")
        cluster_relations = defaultdict(lambda: {'related': 0, 'total': 0})

        # Count related documents per cluster
        for filename, details in results['related']:
            cluster = details.get('cluster')
            if cluster is not None:
                cluster_relations[cluster]['related'] += 1
                cluster_relations[cluster]['total'] += 1
        # Count non-related documents per cluster
        for filename, details in results['not_related']:
            cluster = details.get('cluster')
            if cluster is not None:
                cluster_relations[cluster]['total'] += 1
        # Print statistics
        for cluster in sorted(cluster_relations.keys()):
            rel = cluster_relations[cluster]['related']
            tot = cluster_relations[cluster]['total']
            print(f"Cluster {cluster}: {rel}/{tot} related ({rel / tot * 100:.1f}%)")


if __name__ == "__main__":
    directory_path = os.path.join(os.path.dirname(__file__), "test")  # Change to your folder
    results = analyze_texts_in_directory(directory_path)
    print_results(results)