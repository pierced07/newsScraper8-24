from transformers import pipeline, BartTokenizer

# Initialize the tokenizer and summarizer
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def count_tokens(text):
    """Counts the number of tokens in the text using the BART tokenizer."""
    tokens = tokenizer.encode(text, return_tensors="pt")
    return tokens.shape[1]

def chunk_text(text, max_tokens=1024, min_chunk_tokens=500):
    """Splits text into chunks that are within the max token limit and handles short chunks."""
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = count_tokens(sentence)
        if current_length + sentence_length <= max_tokens:
            current_chunk.append(sentence.strip())
            current_length += sentence_length
        else:
            if current_length >= min_chunk_tokens:
                chunks.append('. '.join(current_chunk).strip() + '.')
            current_chunk = [sentence.strip()]
            current_length = sentence_length

    if current_chunk:
        last_chunk = '. '.join(current_chunk).strip() + '.'
        if count_tokens(last_chunk) < min_chunk_tokens:
            if chunks:
                previous_chunk = chunks.pop()
                combined_chunk = previous_chunk + ' ' + last_chunk
                while count_tokens(combined_chunk) > max_tokens:
                    split_point = len(combined_chunk.split()) // 2
                    chunks.append(' '.join(combined_chunk.split()[:split_point]))
                    combined_chunk = ' '.join(combined_chunk.split()[split_point:])
                chunks.append(combined_chunk)
            else:
                chunks.append(last_chunk)
        else:
            chunks.append(last_chunk)

    return chunks

def summarize_text(text):
    """Summarizes long text by splitting it into smaller chunks and summarizing each chunk."""
    # Split the text into manageable chunks
    chunks = chunk_text(text)

    # Summarize each chunk and combine the results
    summary = []
    for chunk in chunks:
        chunk_summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summary.append(chunk_summary[0]['summary_text'].strip())

    # Combine all the chunk summaries into one final summary
    final_summary = ' '.join(summary)
    return final_summary

# Example usage
text = """ """  # Use your actual text here
summary = summarize_text(text)
print(summary)
