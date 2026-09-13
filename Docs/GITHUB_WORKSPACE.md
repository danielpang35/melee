# GitHub publication policy

13 September 2026. Daniel uses this repository for GPT-6 Pro-assisted development and art review. Publish current source, configuration, tests, tools, design/technical documents, selected small authoring controls/receipts, and curated ordinary-image review media. Exclude archived animation drafts and large native/binary assets from the current GitHub tree. Preserve all of them in the complete local workspace.

The [review entry point](GITHUB_REVIEW.md) explains scope and the [art gallery](Review/README.md) identifies selected visible evidence. Historical source paths and tests still refer to the full authoring workspace. Their absence here is a publication decision, not deletion of local source or proof that the game can run without assets.

`Tools/PrepareGitHubReview.py prepare` creates a reviewable snapshot under ignored Saved. Its explicit `commit` step creates a separate publication branch using an alternate index and the verified current remote parent. It does not switch the authoring branch, overwrite its index, remove local files, push, or rewrite remote history. Review the manifest, then push that publication branch to main without force. Never push the full local archive commit as its parent: that would make the binary archive reachable again.

The first interrupted upload may have transferred unreferenced LFS objects; no asset-bearing commit was published. Existing remote history is retained, so this policy concerns the current tree and future publication, not a purge of already-published historical objects.
