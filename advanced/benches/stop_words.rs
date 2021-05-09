use std::fs;

use criterion::{black_box, criterion_group, criterion_main, Criterion};

use patricia_tree::PatriciaSet;
use std::collections::HashSet;

fn criterion_benchmark(c: &mut Criterion) {
    let data = fs::read_to_string(
        "/Users/halvorbo/Projects/search-engine/data/corpus/stop_words_english.txt",
    )
    .expect("Unable to read file");
    let mut trie_set = PatriciaSet::new();
    let mut hash_set = HashSet::new();
    for word in data.split("\n") {
        trie_set.insert(word);
        hash_set.insert(word);
    }
    c.bench_function("trie foo", |b| {
        b.iter(|| trie_set.contains(black_box("foo")))
    });
    c.bench_function("trie the", |b| {
        b.iter(|| trie_set.contains(black_box("the")))
    });
    c.bench_function("trie pneumonoultramicroscopicsilicovolcanoconiosis", |b| {
        b.iter(|| trie_set.contains(black_box("pneumonoultramicroscopicsilicovolcanoconiosis")))
    });
    c.bench_function("hash foo", |b| {
        b.iter(|| hash_set.contains(black_box("foo")))
    });
    c.bench_function("hash the", |b| {
        b.iter(|| hash_set.contains(black_box("the")))
    });
    c.bench_function("hash pneumonoultramicroscopicsilicovolcanoconiosis", |b| {
        b.iter(|| hash_set.contains(black_box("pneumonoultramicroscopicsilicovolcanoconiosis")))
    });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
