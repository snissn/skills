# Profiling And Measurement

Adapt these examples to the repository's pinned toolchain, package, benchmark, and
runner. They are templates, not a mandatory matrix. Check flags against the target
Go version. Prefer an existing maintained public harness over adding another one.

## Comparable Runs

Record source SHA plus dirty diff or overlay bytes, build flags/tags/PGO inputs,
Go version and relevant environment (`GOOS`, `GOARCH`, `GOMAXPROCS`, `GOGC`,
`GOMEMLIMIT`, `GODEBUG`, module/workspace/toolchain selection), host/CPU, affinity,
and fixture seed/shape/state. Keep non-product inputs identical; identify the
intended source delta. Preserve binary hashes, exact argv, exit status, and raw
stdout/stderr. Do not expose secrets while recording environment.

Compile baseline and candidate independently before the timed window, using the
same harness. A shared benchmark-only overlay is useful when the old source lacks
the harness; retain its exact bytes and both effective input sets. Never transplant
candidate production code into the baseline by accident.

```sh
# In each source checkout, with the selected toolchain/environment:
go test -c -o /evidence/before.test ./path/to/package
# Build the candidate analogously as /evidence/after.test.

# Use a fresh evidence directory; increment 01 for each planned alternating pair.
/evidence/before.test -test.run='^$' -test.bench='^BenchmarkPublicOperation$' \
  -test.benchmem -test.benchtime=1s -test.count=1 \
  > /evidence/before-01.txt 2> /evidence/before-01.stderr
/evidence/after.test -test.run='^$' -test.bench='^BenchmarkPublicOperation$' \
  -test.benchmem -test.benchtime=1s -test.count=1 \
  > /evidence/after-01.txt 2> /evidence/after-01.stderr
# After collecting every planned pair, combine each side's retained stdout.
cat /evidence/before-*.txt > /evidence/before.txt
cat /evidence/after-*.txt > /evidence/after.txt
benchstat /evidence/before.txt /evidence/after.txt
```

Use fixed iterations (for example `-test.benchtime=1000x`) when equal operation
counts are needed to preserve a growing workload or match attribution. Time-based
calibration can execute different amounts of work and reset/reenter a benchmark;
inspect fixture lifetime. Either approach still needs equivalent state and enough
work for its purpose. Recreate fixtures outside timing or document their reuse.
Stop/start/reset benchmark timers exclude harness work from benchmark accounting,
not necessarily from process-wide profiles. Confirm what `B/op` includes, including
background work during the interval. Match setup, forced GC, warmup, and cleanup
policy between sides; do not use artificial GC/cache conditions as production proof.

Short pairs are diagnostic. For final statistical claims, preselect sample count
and duration appropriate to noise and effect size. [Benchstat guidance](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat)
recommends repeated, interleaved samples; retain dispersion/uncertainty and avoid
selective reruns. A stable byte count does not make a short latency sample conclusive.
Operations/s = 1e9 / ns/op for the same operation; batch operations are not individual
records unless the actual batch size is included.

## Select Instrumentation For The Question

Use separate bounded invocations for the needed instrument. Do not compare these
timings with uninstrumented results or combine every expensive profiler at once.
These examples use the already built candidate and the same public workload:

```sh
/evidence/after.test -test.run='^$' -test.bench='^BenchmarkPublicOperation$' \
  -test.benchtime=1s -test.cpuprofile=/evidence/cpu.pprof
/evidence/after.test -test.run='^$' -test.bench='^BenchmarkPublicOperation$' \
  -test.benchtime=1000x -test.memprofile=/evidence/alloc.pprof -test.memprofilerate=1
/evidence/after.test -test.run='^$' -test.bench='^BenchmarkPublicOperation$' \
  -test.benchtime=1s -test.mutexprofile=/evidence/mutex.pprof -test.mutexprofilefraction=1
/evidence/after.test -test.run='^$' -test.bench='^BenchmarkPublicOperation$' \
  -test.benchtime=1s -test.blockprofile=/evidence/block.pprof -test.blockprofilerate=1

go tool pprof -top /evidence/after.test /evidence/cpu.pprof
go tool pprof -top -alloc_space /evidence/after.test /evidence/alloc.pprof
go tool pprof -top -alloc_objects /evidence/after.test /evidence/alloc.pprof
go tool pprof -top -inuse_space /evidence/after.test /evidence/alloc.pprof
go tool pprof -top -cum /evidence/after.test /evidence/cpu.pprof
```

Full allocation/event sampling can heavily perturb runtime and produce large
artifacts. Use it for a short attribution run only when the extra detail is needed;
otherwise choose an adequate sampling rate. For mutex/block work, reproduce relevant
concurrency; a single-worker benchmark cannot establish contention improvements.
Mutex profiles identify contended lock holders; block profiles identify waiting
sites. Their summed waiter time can exceed wall time. Use execution trace when
scheduling, GC phases, serialization, or asynchronous work need a timeline. CPU
samples show executing cost, not elapsed waiting or I/O latency.

See official [Go diagnostics](https://go.dev/doc/diagnostics),
[test flags](https://pkg.go.dev/cmd/go#hdr-Testing_flags), and
[pprof usage](https://github.com/google/pprof/blob/main/doc/README.md) for the
appropriate capture controls; do not expose a public profiling endpoint merely to
diagnose a local workload.

## Interpret The Denominator

For every number, name the profile/sample type, absolute units, capture interval,
operation count, and filtering. An allocation profile may include initialization,
fixtures, stopped-timer flushes, and teardown that benchmark `B/op` excludes.
Use a verified region/delta capture when feasible or separate public-operation
stacks and report the remaining scope. Do not divide whole-process allocation by
benchmark iterations and call it exact operation allocation without establishing
that boundary. Compare like scopes and sampling settings between source versions.

Flat cost belongs to a specific sampled site; cumulative cost includes descendants.
Cumulative parent and child rows overlap. Attribute a subsystem with a named union
of disjoint flat sites/stacks, retaining before/after absolute values and the total
denominator. If inlining or shared sites blur attribution, inspect source/assembly
or call stacks and disclose the ambiguity; do not count it twice. A percentage can
rise while absolute cost falls because the denominator shrank. Normalize only
when the work and capture scope justify it. Additive component savings must not be
inferred from separate cumulative profiles or successive baselines.

Allocation space/objects measure churn, including freed objects; in-use
space/objects describe live sampled allocations, subject to GC timing. Neither is
process RSS or a peak-memory measurement. Compare retention at equivalent lifecycle
points and GC conditions; inspect backing-array aliases, long-lived owners, cache
bounds, and pool contents if churn fell but live memory grew. Review the
[runtime profile definitions](https://pkg.go.dev/runtime/pprof#Profile) and
[`sync.Pool` contract](https://pkg.go.dev/sync#Pool) when those distinctions matter.

For an incremental variant, change only the mechanism under test and preserve
necessary detach/copy/fallback work and semantics. Bind variant files/overlay map
and effective build inputs. An activation test deliberately disabling that
mechanism may fail by design; do not report that variant as correctness-qualified.
Final public gains come from the integrated candidate's matched A/B, not sums of
isolated attribution experiments.
