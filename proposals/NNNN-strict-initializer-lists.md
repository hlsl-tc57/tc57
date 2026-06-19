---
title: NNNN - Strict Initializer Lists
params:
  authors:
  - llvm-beanz: Chris Bieneman
  sponsors:
  - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Introduction

HLSL should adopt C and C++ initializer list parsing rules, rather than
custom rules that are unintuitive and error-prone.

## Motivation

HLSL supports flattened brace initialization such that the structure of the
bracket initializer on the right-hand side of an initialization is ignored, and
only the number of initialization arguments matters. Further, vector and matrix
arguments are implicitly expanded.

This feature likely results in a variety of common errors as HLSL will attempt
to fit an initializer list to a structure regardless of the underlying structure
of the members.

In HLSL the following code is valid:

  struct A {
    int a;
    double b;
  };
  struct B {
    A a[2];
    int c;
  };
  B b = {{1, 1.2}, {2, 2.2}, 3};   // Array elements specified as members
  B b2 = {1, 2, 3, 4, 5};          // each field initialized separately
  B b3 = {{1, {2, 3}}, {4, 5}};    // Completely random grouping of arguments
  int4 i4 = {1,2,3,4};             // valid int4 in C-syntax
  B b4 = {i4, 5};                  // int4 implicitly expanded to 4 arguments
```

Formalizing this code to comply with C/C++ initializer list rules will likely
break existing code, however following C/C++ rules will allow error checking and
validation of initializer lists which is likely to catch bugs which may be
difficult to identify otherwise.

## Proposed solution

Adopt C & C++ initializer list rules, and remove HLSL-specific initialization
list behaviors. Specifically, this will remove implicit vector and structure
element extraction, and enforce type system rules for data types passed into
initializer lists.

This will also introduce C rules for zero-initialization including zero
initialization for structure members omitted from the initialization list.

### Forward-source breaking

This change will be forward source breaking, and backwards compatible with some
caveats. Current code that takes advantage of HLSL initialization semantics will
produce an error, but implementations should be able to automate migration
through tooling. Code updated to support the new syntax should be mostly
backward compatible to older HLSL versions as long as each structure is fully
initialized.

For example given the source example from the motivation section above, a tool
could rewrite the initializers as:

  B b = {{{1, 1.2}, {2, 2.2}}, 3};
  B b2 = {{{1, 2}, {3, 4}}, 5};
  B b3 = {{{1, 2}, {3, 4}}, 5};
  int4 i4 = {1,2,3,4};
  B b4 = {{{i4.x, i4.y}, {i4.z, i4.w}}, 5};
```

The rewritten initializers all behave the same but shift braces to match
structure layouts and explicitly expand aggregate members.

### Non-backward compatible uses

New code that takes advantage of C & C++'s zero-initialization behavior or
relies on user-defined conversion functions will not be backwards compatible to
older HLSL versions.

For example:

```c++
struct S {
  int X[2];
  operator float() {
    return ((float)X[0])/((float)X[1]);
  }

  operator double() {
    return (float)this;
  }
};

struct F {
  float2 f;
};

struct D {
  double3 f;
};

S s1 = {{1,2}}; // Valid with and without this change.
S s2 = {};      // Invalid without and valid with this proposal, zero-initializes all members.
S s3 = {1};     // Invalid without and valid with this proposal, zero-initializes unspecified members.
F f1 = {s1};    // Invalid without and valid in both cases, but the meaning changes. Without this proposal f1 is initialized to {1,2}, with this proposal it is initialized to {0.5, 0}.
D d1 = {s1};    // Invalid without and valid with this proposal, initializes to {0.5,0,0}.
```
