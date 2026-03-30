def runs_chunker_with_overlap(run_texts, num_runs=50, runs_overlap=0):
    chunks = []
    for i in range(0, len(run_texts), num_runs - runs_overlap):
        lpos = max(0, i - runs_overlap)
        rpos = min(i - runs_overlap + num_runs, len(run_texts))
        chunks.append(run_texts[lpos:rpos])
    return chunks


def transform_big_chunks(texts, function):
    new_texts = []
    for chunk in runs_chunker_with_overlap(texts):
        processed_chunk = function("➡️".join(chunk)).split("➡️")

        delta_runs = len(processed_chunk) - len(chunk)

        if delta_runs > 0:
            processed_chunk = processed_chunk[: len(chunk)]
        elif delta_runs < 0:
            processed_chunk += [""]*(-delta_runs)

        new_texts += processed_chunk
    return new_texts
