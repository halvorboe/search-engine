
mode = Mode.OR 
pointer = 0

while pointer < len(query_expressions):
    query_expression = query_expressions[pointer]
    if query_expression in MODES:
        # set mode
    else:
        if query_expression == QUOTE:
            # handle EXACT CASE
            new_document_scores = ...
            # set pointer to the location of the closing quote 
        else:
            # handle TERM CASE
            new_document_scores = ...
        # update the global variables variables 
        # using new_document_scores and the mode
        # AND, OR, INCLUDE, EXCLUDE
    pointer += 1

# compute the final scores
# filter out based on exclusion and inclusion

pointer += 1

matches = [
    (document_id, token_position + 1)
    for document_id, token_position in inverted_index.get(
        query_expressions[pointer], []
    )
]

pointer += 1

while query_expressions[pointer] != QUOTE:
    if not matches:
        break
    term = query_expressions[pointer]
    matches = next_token_position_matches(inverted_index[term], matches)
    pointer += 1

document_term_scores = term_scores(token_positions)
