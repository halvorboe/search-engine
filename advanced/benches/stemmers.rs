use rust_stemmers::{Algorithm, Stemmer};

use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn criterion_benchmark(c: &mut Criterion) {
    let en_stemmer = Stemmer::create(Algorithm::English);
    c.bench_function("stem fruitlessly", |b| {
        b.iter(|| en_stemmer.stem(black_box("fruitlessly")))
    });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
