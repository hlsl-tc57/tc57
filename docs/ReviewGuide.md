---
title: Review Guide
---

This document provides guidance on how to conduct reviews of PRs contributed to
TC57. TC57's main work product is a technical specification for the HLSL
programming language, and reviewing specification text and proposal documents is
different from reviewing code.

There are different types of PRs that posted to TC57 on a regular basis, and
each have different relevant considerations. The sections below broadly classify
categories of PRs. Some PRs may fall into more than one category, although
generally speaking authors should try to avoid that where possible (notably
editorial and technical changes may frequently be interdependent).

## General Guidelines

The purpose of a review is to assist the author and ensure that the work product
of TC57 is the highest quality possible. PR reviews are the primary method of
iteration for TC57, as such frequent and prompt feedback is critically
important.

Because PRs changing specification text and proposal states require approval by
the committee in an official meeting; providing feedback on those PRs as early
as possible is essential. This allows authors to adapt to feedback and the
committee delegates to review the updated PRs. This does not mean that the
committee will ignore or reject late-arriving feedback; late-arriving feedback
will hinder the committee's ability to move forward.

### Simple Guidance

* Do assume good faith.
* Do provide both constructive and positive feedback.
* Do ask clarifying questions.
* Do suggest specific changes.
* Do provide specific examples.
* Do provide context and rationale.
* Don't make vague comments.
* Don't make value statements.

Comments on PRs should be _specific and actionable_. When a reviewer leaves a
comment, it should be clear to anyone with limited context whether the reviewer
is requesting a change to the PR, and either the requested change or problem
needing consideration.

### Primary Concerns

All documents should strive to be clear, accurate, and consistent. Feedback to
ensure these criteria is valid on every PR although such feedback need not always
be addressed immediately
(see: [directing feedback](#directing-feedback-for-later) and
[rating importance](#rate-the-importance)).

Correct spelling, grammar, and punctuation is a basis for document clarity as
are some stylistic concerns such as prioritizing brevity and use of concise
language.

### Working on a Standard

As a technical committee of Ecma International TC57 is operating as a standards
making committee, this results in some important restrictions on its activities
which should be considered when providing feedback.

Familiarize yourself with [TC57's charter](https://ecma-international.org/technical-committees/tc57/)
TC57 must operate within the charter which restricts some of the areas where
discussions of the TC may stray.

#### Relevance of Implementations

One notable point is that TC57's charter _does not include_ producing an
implementation of the standard. As such, discussions around specific
implementation details will be frequently out-of-scope. This does not mean the
TC should ignore the existence of implementations as a standard with no
implementations is not useful to anyone, but concretely it means "viability of
implementation" is in-scope while imposing or requiring specific implementation
approaches is not.

### Directing Feedback for Later

Some feedback that a reviewer may provide need not be addressed in the current
PR under consideration. In these cases we ask that the reviewer be proactive in
suggesting that feedback could be addressed later, and when.

For feedback on proposals, feedback can be addressed to a specific proposal
state. For example, a reviewer might say "For refinement: ..." to suggest that a
piece of feedback be tracked and addressed during the refinement stage.
If a reviewer isn't specific about when the feedback needs to be
addressed they could say "Before completion: ..." to request consideration
before a proposal advances to the **Complete** stage.

### Rate the Importance

When leaving feedback consider the importance. From the reviewer's perspective
some feedback may be a "nitpick" that is ignorable or a general comment that
could be addressed in a follow-up neither of which need to block progress.
Other feedback may be "critical" and progress should blocked until it
is resolved. Clearly identifying the importance of feedback allows authors and
sponsors to focus on the highest priority feedback and keep forward progress.

## Technical PRs

Technical PRs may be merged after review by at least one committee delegate.

Some PRs to TC57 are of a technical nature. They may be updates to scripts,
templates, or other machinery involved in operating the committee or producing
final documents.

These changes should be reviewed as you would review any code change with an eye
toward maintainability and technical excellence. There are many great guides on
the internet for how to perform code reviews which can serve as resources such
as:

* [Google's - How to do a code review](https://google.github.io/eng-practices/review/reviewer/)
* [GitHub's blog - How to review code effectively](https://github.blog/developer-skills/github/how-to-review-code-effectively-a-github-staff-engineers-philosophy/)
* [Atlassian's blog - Code review best practices](https://www.atlassian.com/blog/add-ons/code-review-best-practices)

## Editorial PRs

Editorial PRs may be merged after review by at least one
[editor](Officers.md#editor-group). Anyone may notify the editors on a PR or
issue by mentioning the @tc57-editors GitHub Team.

When reviewing editorial changes the first concern should be that the changes
are in fact editorial. Editorial changes may change formatting, spelling,
grammar, punctuation, and minor wording but should _never change
meaning_.

Editorial changes should address a specific issue (such as conforming to style
rules, fixing broken references, correcting spelling, improving formatting for
readability, etc). Editorial changes may frequently have a
[technical](#technical-prs) component since they may require changes to build
scripts, templates or other technical components (this is expected and should
not be discouraged).

## Specification Text PRs

**No substantive change to specification text shall be merged without
approval by the committee at a TC57 meeting.**

Changes to specification text that is not purely editorial will either be
introduced following the [defect process](DefectProcess.md) or the [proposal
process](ProposalProcess.md).

For text introduced through the proposal process the final review during
integration into the specification should be treated as an
[editorial](#editorial-prs) PR because the committee has already approved the
specification text.

For text introduced through the defect process the first consideration should be
that the text accurately and clearly describes the behavior of existing
implementations. **No committee discussions are required for specification
language that matches actively maintained reference implementations**.

## Proposal PRs

**No PR merging a new proposal, or changing the state of a proposal shall be
merged without approval by the committee at a TC57 meeting.**

All proposal PRs should be reviewed for clarity, spelling and grammar. At
different stages in the [proposal process](ProposalProcess.md) reviewers should
have different primary considerations.

### New Proposals

The primary concern for any new proposal PR should be that it contains a basic
description of a problem. It may or may not contain a proposed solution.

The bar for new proposals should be low because the stakes are low (new
proposals have no binding commitment to the standard). There are two specific
questions the committee should answer:

* Should TC57 spend time solving this problem?
* Is there a sponsor within TC57 to drive this (could be the author)?

If both answers are affirmative, TC57 should approve the new proposal.

### Under Consideration

When a proposal is **Under Consideration** reviews should focus on clarity and
viability of the proposed change. Reviewers should not expect all questions to
be answerable at this stage, nor should they expect all the final details to be
resolved.

Reviewers should focus on the reasoning behind the problem statement and the
clarity of the solution.

For stage advancement to **Refinement** the committee will be answering the
questions:

* Is this proposed solution aligned with current goal statements?
  ([202x](HLSL202x,md) or [202y](HLSL202y.md))
* Do we have reasonable confidence in this proposal?

The later question is difficult to provide specific guidance to reviewers on as
it inherently relies on feedback from differing perspective. TC57 delegates will
be asked to assess if they think the proposal is _a likely correct direction_
for HLSL. This does not need absolute certainty, but we also don't want to waste
time by allowing proposals to move forward with low probability of success.

### Refinement

When a proposal is in **Refinement** the authors are drafting proposed language
to be included in the specification. This is the most critical phase of a
proposal for review.

Reviewers should focus on the accuracy of the drafted specification language as
this will be integrated to the specification text after the proposal is
**Accepted**.

For stage advancement to **Completed** the committee will be looking to see
that all issues against the PR which will require specification text are
resolved.

The committee will be asked for approval to include the proposed specification
text in the draft specification for inclusion in the next release of the
specification.

### PRs to Accepted and Completed Proposals

PRs to Accepted and Completed proposals should only be for minor editorial
updates (clarifications, spelling, grammar, etc), or to update progress notes or
other proposal metadata.

These PRs should be reviewed as [editorial](#editorial-prs) changes.
