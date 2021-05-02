from typing import List, Dict, Tuple, Set, Optional
from enum import Enum, auto
import pathlib
import re
from itertools import chain
import time


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print(
            "{:s} function took {:.3f} ms".format(f.__name__, (time2 - time1) * 1000.0)
        )

        return ret

    return wrap


DocumentId = int
Score = int
Term = str
Query = str
Position = int
TokenPosition = Tuple[DocumentId, Position]
TokenPositions = List[TokenPosition]
DocumentScores = Dict[DocumentId, Score]
InvertedIndex = Dict[Term, TokenPositions]
QueryResult = List[Tuple[DocumentId, Score]]

document_path = pathlib.PosixPath("performance")

documents = []
names = {}

for document_id, path in enumerate(document_path.iterdir()):
    names[document_id] = path.stem
    with path.open() as f:
        documents.append(f.read())


# Analyze


def tokenize(document: str) -> List[str]:
    # convert the document to lowercase
    lowercase_document = document.lower()
    # extract all the words using a regex
    words = re.findall(r"\w+", lowercase_document)
    return list(words)


tokenized_documents = [tokenize(document) for document in documents]

# for tokenized_document in tokenized_documents:
#    print(tokenized_document[:3], "...", tokenized_document[-3:])

# Index

inverted_index: InvertedIndex = {}

for document_id, tokenized_document in enumerate(tokenized_documents):
    for token_index, token in enumerate(tokenized_document):
        token_position = (document_id, token_index)
        if token in inverted_index:
            inverted_index[token].append(token_position)
        else:
            inverted_index[token] = [token_position]

# print("just ->", inverted_index["just"])
# print("do ->", inverted_index["do"])

# Query


class Mode(Enum):
    AND = auto()
    EXCLUDE = auto()
    INCLUDE = auto()
    OR = auto()


MODES = {
    "+": Mode.INCLUDE,
    "-": Mode.EXCLUDE,
    "AND": Mode.AND,
}
QUOTE = '"'


@timing
def query_index(inverted_index: InvertedIndex, query: Query) -> QueryResult:
    # STEP 1: Extract out all the
    query_expressions = re.findall(r"[\"\-\+]|[\w]+", query)

    # print(query_expressions)

    # the score of each document
    document_scores: DocumentScores = {}
    # the documents that have been excluded using - or +
    excluded_document_ids: Set[DocumentId] = set()
    no_include_in_query = True
    included_document_ids: Set[DocumentId] = set()

    # what mode are we in
    mode = Mode.OR
    # what part of the expression are we currently evaluating
    pointer = 0

    while pointer < len(query_expressions):
        query_expression = query_expressions[pointer]
        if query_expression in MODES:
            mode = MODES[query_expression]
            pointer += 1
            continue
        elif query_expression == QUOTE:
            try:
                end_index = query_expressions[pointer + 1 :].index(QUOTE)
            except ValueError:
                # if there is no end we ignore the character
                pointer += 1
                continue
            query_expression = [
                term.lower()
                for term in query_expressions[pointer + 1 : pointer + end_index + 1]
            ]
            # in case it's an empty parentasis
            if not query_expressions:
                pointer += 1
                continue
            # find all the initial matches
            first_term, terms = query_expression[0], query_expression[1:]
            matches = [
                (document_id, token_position + 1)
                for document_id, token_position in inverted_index.get(first_term, [])
            ]
            # for each term, find the remaining matches
            for term in terms:
                if not matches:
                    break
                if term not in inverted_index:
                    matches = []
                    break
                matches = token_position_matches(inverted_index[term], matches)

            document_term_scores = term_scores(matches)

            pointer += end_index + 1
        else:
            term = query_expression.lower()
            if term in inverted_index:
                document_term_scores = term_scores(inverted_index[term])
            else:
                document_term_scores = {}

        # print("mode", mode, document_scores)
        if mode == Mode.EXCLUDE:
            excluded_document_ids.update(document_term_scores.keys())
            mode = Mode.OR
        elif mode == Mode.INCLUDE:
            no_include_in_query = False
            included_document_ids.update(document_term_scores.keys())
            merge_or(document_scores, document_term_scores)
            mode = Mode.OR
        elif mode == Mode.OR:
            merge_or(document_scores, document_term_scores)
        elif mode == Mode.AND:
            merge_and(document_scores, document_term_scores)
            mode = Mode.OR
        else:
            raise ValueError(f"unknown mode {mode}")

        pointer += 1

    return list(
        sorted(
            (
                (document_id, score)
                for document_id, score in document_scores.items()
                if (no_include_in_query or document_id in included_document_ids)
                and document_id not in excluded_document_ids
            ),
            key=lambda x: -x[1],
        )
    )


def term_scores(token_positions: TokenPositions) -> DocumentScores:
    # number of times term appears in document
    document_term_scores: DocumentScores = {}
    for document_id, _ in token_positions:
        if document_id in document_term_scores:
            document_term_scores[document_id] += 1
        else:
            document_term_scores[document_id] = 1
    return document_term_scores


def merge_or(current: DocumentScores, new: DocumentScores):
    for document_id, score in new.items():
        if document_id in current:
            current[document_id] += score
        else:
            current[document_id] = score


def merge_and(current: DocumentScores, new: DocumentScores):
    # Find the keys that are not in both.
    filtered_out_documents_ids = set(current.keys()) ^ set(new.keys())
    for document_id in list(current.keys()):
        if document_id in filtered_out_documents_ids and document_id in current:
            del current[document_id]
    for document_id, score in list(new.items()):
        if document_id not in filtered_out_documents_ids:
            current[document_id] += score


def token_position_matches(
    token_positions: TokenPositions, expected_token_positions: TokenPositions
) -> TokenPositions:
    # returns position of next expected match
    matches = []
    # create mapping from current expected to next expected
    next_expected_token_positions = {
        (document_id, token_position): (document_id, token_position + 1)
        for document_id, token_position in expected_token_positions
    }
    for position in token_positions:
        if position in next_expected_token_positions:
            matches.append(next_expected_token_positions[position])

    return matches


queries: List[Query] = [
    "just do",
    "just AND do",
    '"just do" AND it',
    '+"just do" AND tomorrow',
    "-just do",
    'do AND "you can" -tomorrow',
]

for query in queries:
    print(
        query,
        "\n"
        + str(
            [
                (document_id, names[document_id], score)
                for document_id, score in query_index(inverted_index, query)
            ][:3]
        ),
    )


@timing
def iterate_documents():
    a = ["just", "do"]
    count = 0
    for d in tokenized_documents:
        for t in d:
            for c in a:
                if c == t:
                    count += 1
    return count


print(iterate_documents())
