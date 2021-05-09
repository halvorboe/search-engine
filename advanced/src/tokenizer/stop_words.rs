// https://github.com/tantivy-search/tantivy/blob/main/src/tokenizer/stop_word_filter.rs

mod tests {

    use criterion::{black_box, criterion_group, criterion_main, Criterion};

    fn fibonacci(n: u64) -> u64 {
        match n {
            0 => 1,
            1 => 1,
            n => fibonacci(n - 1) + fibonacci(n - 2),
        }
    }

    fn criterion_benchmark(c: &mut Criterion) {
        c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
    }

    criterion_group!(benches, criterion_benchmark);
    criterion_main!(benches);
    use patricia_tree::PatriciaMap;

    fn test_trie() {
        let mut map = PatriciaMap::new();
        map.insert("foo", 1);
        map.insert("bar", 2);
        map.insert("baz", 3);
        assert_eq!(map.len(), 3);

        assert_eq!(map.get("foo"), Some(&1));
        assert_eq!(map.get("bar"), Some(&2));
        assert_eq!(map.get("baz"), Some(&3));
    }
}
