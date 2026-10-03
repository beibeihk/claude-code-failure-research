# Privacy and evidence handling

Raw stdout, stderr, transcripts, complete upstream issue bodies and working
repositories stay in ignored `.private/`. They are never staged or published.
Auth files are neither read into logs nor copied into the project. The runner
preserves the real Codex and Claude credential stores and never logs credentials.

Public run exports omit claim text and retain only a hash, classification and
verifier metadata. The redactor covers home paths, emails, common token formats,
authorization headers, password/cookie fields, JWTs, phones, URL credentials and
explicit private literals. This is a defense in depth, not a general proof that
arbitrary prose contains no sensitive information.

Inspect each export for names, account IDs, private repository names, hostnames,
private conversation fragments and secrets not caught by patterns. The exporter
requires an explicit researcher review flag; no command pushes an export. Publish
only short, necessary evidence excerpts in a later reviewed case. Full transcripts
are out of scope even when a redactor produces clean-looking text.

Hashed session/tool identifiers remain linkable pseudonymous data. Limit their
scope to a study and do not treat hashing as a guarantee of anonymity.

Privacy scanning of result/report metadata is part of offline validation. Test
files contain synthetic redaction examples; these are not real credentials.
Official source snapshots are excluded from publication and license coverage.

No security exploit has been investigated or found in this phase. If a future
candidate crosses a security boundary, stop public dissemination and use the
current official private channel. The public lab must not contain exploit chains,
credential extraction details or a sandbox/permission bypass reproduction.
