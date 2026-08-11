---
title: 0010 - Modern C++ Features
params:
  authors:
  - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

* Issues:
   * auto: [#24](https://github.com/microsoft/hlsl-specs/issues/24)
   * decltype: [#82](https://github.com/microsoft/hlsl-specs/issues/82)
   * constexpr: [#21](https://github.com/microsoft/hlsl-specs/issues/21)
[#74](https://github.com/microsoft/hlsl-specs/issues/74)
   * variadic templates: [#21](https://github.com/microsoft/hlsl-specs/issues/21)
   * static assert: [#33](https://github.com/microsoft/hlsl-specs/issues/33)
   * simplified nested namespace: [#68](https://github.com/microsoft/hlsl-specs/issues/68)

## Implementation Status

|   | DXC     | Clang    |
|---|---------|----------|
| C++11 template closing `>>` | Complete  | Complete |
| variadic templates | Not Started | Complete |
| variable templates | Not Started | Not Started |
| `auto` keyword | Complete  | Complete |
| decltype | Not Started | Complete |
| Return type deduction for normal functions | Not Started | Not Started |
| constexpr | [Prototype](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/c78e5916454521714f182b55abc48df0f3e96edb) | Complete |
| static_assert | [Prototype](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/db275103054bf8ac2336f4ea2e693e610de70702) | Complete |

## Introduction

In DXC HLSL is a set of feature extensions on top of a subset of C++98. C++98
is now over 20 years old and most modern C++ users have adopted newer language
constructs. This proposal suggests integrating high-impact modern C++ features
that should be low-cost to implement.

## Motivation

HLSL's C++ base is over a decade old. Modern C++ features have been frequently
requested additions for HLSL. Features introduced in C++11 and C++14 have been
in use for over a decade and are widely adopted. C++17 is nearly a decade old
now as well, and also has many widely adopted features. Conversely C++98 has
some oddities that are unusual and unexpected to developers who may have started
their career after modern C++ was widely adopted.

## Proposed solution

This proposal introduces a small number of targeted modern C++ features for HLSL
which improve and extend the capabilities of HLSL 2021 while reducing friction
bridging between HLSL and C++.

### Modern Template

C++11 and C++14 introduced several valuable extensions to C++'s template
support which HLSL will adopt.

HLSL will adopt the template parsing rules allowing closing template brackets
(`>>`) to be adjacent without whitespace separating the tokens. This feature was
adopted to C++11 in the paper [Right Angle Brakcets
(n1757)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2005/n1757.html).

HLSL will adopt C++'s variadic templates. This feature was adopted to C++11 in
the paper [Proposed Wording for Variadic Templates
(n2242)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2242.pdf).

HLSL will adopt C++'s variable templates. This feature was adopted to C++14 in
the paper [Variable Templates
(n3651)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3651.pdf).

Collectively these features allow modernization of C++ template meta-programming
patterns to align mostly with modern C++ in terms of expressiveness and
capabilities.

### Type deduction with `auto` and `decltype`

HLSL will adopt C++'s `auto` and `decltype` keywords. These features were
adopted to C++11 in the paper [Decltype and auto
(n1607)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2004/n1607.pdf).

HLSL will also adopt C++'s simplifications of return type deduction for
functions. This feature was adpoted to C++14 in the paper [Return type deduction
for normal functions
(n3638)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3638.html).

These features enable additional patterns of meta-programming building off C++
templates and allowing for more concise readable code.

### Compile-time evaluation

C++11 introduced a set of features which subsequent versions have built on to
enable compile-time evaluation of portions of programs and compile-time
verification.

HLSL will adopt the `constexpr` keyword and the associated behaviors introduced
to C++11 in the paper [Generalized constant expressions
(n2235)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2235.pdf).

To allow using generalized constant expressions for compile-time correctness
testing HLSL will adopt the `static_assert` feature adopted to C++11 in the
paper [Proposal to Add Static Assertions to the Core Language
(n1720)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2004/n1720.html).

Additionally we adopt the additions to `static_assert` adopted to C++17 in the
paper [Extending `static_assert`
(n3928)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n3928.pdf).

These features enable robust compile-time expressions and testability of
assumptions which will enable developers to detect errors earlier and write more
maintainable code without hard-coded assumptions.

## Appendix A: Listing of C++ Features Considered

### C++11

HLSL should integrate the following C++11 features ([Source](https://en.cppreference.com/cpp/11)):

* auto - Implemented in both DXC and Clang
* decltype
* constexpr
  * [DXC Prototype](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/c78e5916454521714f182b55abc48df0f3e96edb)
* variadic templates
* Static assert
  * [DXC Prototype](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/db275103054bf8ac2336f4ea2e693e610de70702)
* Template parsing rules (no required space in `>>`)

#### C++11 Excluded Features

* Range-based for loops (grammar ambiguity with HLSL annotations)
* C++11 attributes (will be a separate larger proposal)
* Defaulted and deleted functions (requires constructors)
* C++ list initialization (requires revamping HLSL initialization)
* type aliases (already in HLSL 2021)
* `alignof` and `alignas` (requires target bytecode changes)
* Lambda expressions (will require a separate larger proposal due to type system
  changes)
* C++11 scoped enumerations (will be a separate proposal)
* user-defined literals (deferred)
  * User-defined literals prompted numerous defect reports to WG21, addressing
    those is out-of-scope for HLSL 202x.

### C++14

C++14 features that we could consider ([Source](https://en.cppreference.com/cpp/14)):

* variable templates
* relaxed restrictions on constexpr functions
* binary literals
* digit separators
* return type deduction for functions
  * [DXC Prototype](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/594f9cdcd9379ec7637e0c3467e2d9407f332b55)

#### C++14 Excluded features

* generic lambdas (requires lambdas)
* lambda init-capture (requires lambdas)
* new/delete elision (requires new/delete)
* aggregate classes with default non-static member initializers (requires constructors)

### C++17

C++17 features that we could consider ([Source](https://en.cppreference.com/cpp/17)):

* compile-time `if constexpr`
* initializers for if and switch
* [temporary materialization](https://en.cppreference.com/cpp/language/implicit_conversion#Temporary_materialization)
* structured bindings (assignment decomposition)
* Templates
  * fold-expressions ( ... )
  * class template argument deduction tuple t(4, 3, 2.5)
  * non-type template parameters declared with auto
* Namespaces
  * simplified nested namespaces
  * using-declaration declaring multiple names
  * attribute namespaces don't have to repeat
* new attributes:
  * [[fallthrough]]
  * [[maybe_unused]]
  * [[nodiscard]]
* __has_include

#### C++17 Excluded Features

* u8 character literal (HLSL does not have 8-bit types)
* made noexcept part of type system (HLSL does not have exceptions)
* new order of evaluation rules (these changes don't apply to HLSL)
* lambda capture of *this (requires lambdas)
* constexpr lambda (requires lambdas)
* inline variables (requires linkage model changes)
* guaranteed copy elision (requires construction & rvalue references)

### C++20 and later

Adopting C++ 20 and later features is not under consideration at this time due
to feasibility in existing implementations.
