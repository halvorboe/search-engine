use criterion::{black_box, criterion_group, criterion_main, Criterion};
use regex::Regex;

fn criterion_benchmark(c: &mut Criterion) {
    let document = "the red fox jumped over the big fence";
    let document_string = document.to_owned();
    let regex = Regex::new(r"\s").unwrap();
    c.bench_function("string split", |b| {
        b.iter(|| document_string.split_whitespace());
    });
    c.bench_function("regex split", |b| {
        b.iter(|| regex.split(black_box(document)));
    });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
