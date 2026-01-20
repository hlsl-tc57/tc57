---
title: Proposal Process
---

Despite the openness of this process there are two significant caveats that
should be noted:

1. Final decisions about what proposals are included or excluded from HLSL are
   made by TC57, which is open to all Ecma members.
2. This process does not include HLSL API-specific extensions which are tracked
   separately by API vendors (see: [Vendor Extension Processes](#vendor-extension-processes)).

Proposals from outside TC57 will be interpreted as requests, and may be
considered or rejected based on priorities set by the Technical Committee. You
should not create a pull request against this repository if you're not committed
to at least making a best effort to navigate the process as described below.

If you want to request a feature but not get involved in the process, the best
way to request features for HLSL is to [file GitHub
issues](https://github.com/llvm-beanz/tc/issues/new?template=feature_request.md)
rather than creating pull requests against this repository.

This process draws heavily from
[Rust's RFC process](https://github.com/rust-lang/rfcs),
[Swift's Evolution process](https://github.com/apple/swift-evolution/), and
[Ecma TC39's process](https://tc39.es/process-document/) and is further tweaked
to align with the TC57's goals and priorities.

Significant project infrastructure or implementation details will also use this
process to refine and document the design process.

## Making a Proposal

The best way for an external contributor to propose a feature is through GitHub
issues (See the section below on "Filing Issues").

Every proposal must have a _Sponsor_ who participates in TC57. If the author of
a proposal is not a participant in TC57 the convenor of the next TC57 meeting
will request a volunteer to act the _Sponsor_. The _Sponsor_ is responsible
for tracking and helping change proposals through the proposal life cycle.

All proposals are evaluated against the goals for the targeted HLSL language
revision. At the present moment the committee is tracking two langage versions
provisionally called HLSL 202x and HLSL 202y.

HLSL 202x will be the first Ecma HLSL standard version, it's goal statement can
be found [here](HLSL202x.md). HLSL 202y will be the second Ecma HLSL standard
version, it's goal statement can be found [here](HLSL202y.md).

> Note: We generally do not expect the committee to track more than one version
> at a time, however during the initial standard development we expect to be
> tracking a mixture of behavior changes associated with standardization and
> potential new features. Because we want the initial standard to map closely to
> the existing implementations we are separating the initial standard (202x)
> from the first "feature" update (202y).

When writing a proposal you should also familiarize yourself with the HLSL
[Design Considerations](DesignConsiderations.md).

## Proposal Lifecycle

Draft proposals are first provided as pull requests. They should be written
following one of the templates in the `proposals/templates` directory.

Add new proposals directly in the `proposals` directory. In the initial PR the
proposal should be numbered `NNNN` to signify it has not yet been numbered.

Proposals that follow the most simplified path from idea to finalization will
move through the following states in order:

* **New Proposal** - All proposals begin as new proposals. An initial proposal
  document should describe a problem at a high level and may or may not include
  one or more potential solutions to consider.

* **Under Consideration** - When a proposal is merged into the repository it
  enters the under consideration state. While under consideration proposals are
  reviewed by members of the Ecma TC and feedback is solicited from
  stakeholders. During this time potential solutions are evaluated and a single
  proposed solution is settled on.

* **Refinement** - If TC57 agrees on a path forward for a proposal the proposal
  moves into the refinement phase. During this time, the authors must draft
  proposed specification language. Some proposals may warrant testing within an
  implementation to further prove out the design, that will occur during this
  phase if necessary. Tests for the conformance test suite shall be drafted and
  submitted for review.

* **Accepted** - Once a proposal is accepted it becomes plan of record for the
  next language version. This is the point where the TC recommends that
  maintainers of HLSL compilers implement the proposal. Integration of final
  specification language to the draft specification may occur.

* **Completed** - A proposal is fully integreated into the draft specification
  and will be included in the next standard publication.

Proposals may end up in the **Rejected** or **Deferred** states.

**Rejected** proposals will not be included in HLSL. All rejected proposals will
be appended with a detailed reasoning explaining the rationale behind why the
proposal was rejected.

**Deferred** proposals can occur for a variety of reasons. Proposals that are
deferred may be provided with some justification for the deferral although the
requirements for justification are not high and could be as simple as
"insufficient resources".

### Moving Through States

#### Merging a New Proposal

The bar for a proposal to be merged should be kept low. The proposal must have a
sponsor prior to being merged, and must be approved by the sponsor. A PR
introducing a new proposal should be reviewed for obvious mistakes (typos,
grammar, etc). Reviewers may provide feedback on aspects of the design, however
the author(s) need not address all feedback in the PR before merging. Filing an
issue to follow-up on comments from the initial PR is an acceptable response to
feedback and should be done by the author(s) when resolving comments on the PR.

New proposals should be merged as **Under Consideration**. After assigning a
number and merging the PR the author(s) should file issues tracking the work to
flesh out and complete the detailed design.

PRs introducing new proposals will be reviewed at the next [TC57
Meeting](/docs/Meetings.md).

#### Completing the Detailed Design

As the proposal authors and sponsors work through issues with the proposal and
flesh out a complete design each change to the proposal will be reviewed. The
bar for changes to proposals in the **Under Consideration** phase should be low
to facilitate evolvoing the proposal and addressing issues promptl.

#### Final Review

Once the authors and sponsors feel that all outstanding issues are resolved a
sponsor will and create a PR to mark the proposal as **Refinement**. During this
time the author(s) must draft final specification language and conformance
tests.

#### Accepting a Proposal

On the completion of all outstanding issues, a sponsor will schedule the issue
for an acceptance discussion at a [TC57 meeting](/docs/Meetings.md). On
completion of the discussion the sponsor will either mark the proposal as
**Accepted** or file additional issue to track required changes.

#### Implementation

After a proposal is accepted members of TC57 who represent implementations will
begin implementing a proposal. During implementation a proposal may need to
further evolve as the implementors discover issues or gaps. Those issues will be
addressed with PRs to the proposal and reviewed.

Once the implementation is complete and all associated issues are resolved, a
sponsor will create a PR to merge the final specification language into the
draft specification, and update the state to **Completed**. This change must be
reviewed by the specification editors prior to merging.

## Vendor Extension Processes

DirectX extensions are developed and tracked publicly on [Microsoft's
GitHub](https://github.com/microsoft/hlsl-specs/).

Khronos extensions are developed and tracked under the purview of the Khronos
Vulkan and SPIRV Working Groups. Proposals for Vulkan that are integrated to the
DirectXShaderCompiler also follow the process on [Microsoft's
GitHub](https://github.com/microsoft/hlsl-specs/).
