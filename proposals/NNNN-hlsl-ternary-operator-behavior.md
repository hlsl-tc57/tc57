---
title: NNNN - HLSL Ternary Operator Behavior
params:
    authors:
    - bob80905: Joshua Batista
    sponsors:
    - bob80905: Joshua Batista
    status: Under Consideration
---

* Planned Version: 202x

## Introduction

The value category of the conditional (ternary) operator's result is defined
differently in C and C++. HLSL should clearly specify which behavior it follows,
and should do so consistently across language versions. This proposal specifies
that HLSL adopts the C++ value category rules for the ternary operator going
forward, and documents the divergence between existing HLSL versions.

## Motivation

C and C++ define the value category of the ternary operator's result
differently:

* In C, the result of a ternary operator is always a prvalue (an rvalue).
* In C++, if the second and third operands are both glvalues of the same type,
  the result is a glvalue of that type. This means the result can be the target
  of an assignment.

HLSL does not currently have a clear, consistent specification for this
behavior, and the existing implementation in DXC is buggy. Two distinct bugs are
observable in DXC today:

1. DXC allows an assignment to an rvalue result of the ternary operator.
2. DXC generates a ternary expression whose operands are both glvalues, but
   whose result is incorrectly typed as an rvalue.

The AST dump below demonstrates that DXC produces a `ConditionalOperator` whose
operands are `lvalue` `DeclRefExpr` nodes, while the result of the ternary
itself is an rvalue (note the absence of an `lvalue` annotation on the
`ConditionalOperator`). This was produced with DXC in HLSL 202x mode
(`-T lib_6_5 -HV 202x -ast-dump`,
[Compiler Explorer](https://godbolt.org/z/djz1WK4ed)):

```
| `-ParenExpr 0x61edecdc4378 <col:5, col:18> 'RWByteAddressBuffer'
|   `-ConditionalOperator 0x61edecdc4348 <col:6, col:17> 'RWByteAddressBuffer'
|     |-CXXBoolLiteralExpr 0x61edecdc42e0 <col:6> 'bool' true
|     |-DeclRefExpr 0x61edecdc42f8 <col:13> 'RWByteAddressBuffer' lvalue Var 0x61edecdc4088 'a' 'RWByteAddressBuffer'
|     `-DeclRefExpr 0x61edecdc4320 <col:17> 'RWByteAddressBuffer' lvalue Var 0x61edecdc4148 'b' 'RWByteAddressBuffer'
```

Compounding the problem, the behavior differs between HLSL versions in DXC in a
way that was not intentional. HLSL 2021 has fully custom `SemaHLSL` code for
validating ternary operators, while HLSL 202x currently falls back into the
C++ semantic analysis path. As a result, the same source compiles differently in
DXC depending on the selected language version.

Consider the following example, compiled in DXC with both HLSL 2021 and HLSL
202x ([Compiler Explorer](https://hlsl.godbolt.org/z/j3TcE8Y38)):

```hlsl
export int fn(bool B, int X, int Y) {
    (B ? X : Y) += 1;
    return X;
}
```

In DXC with `-HV 2021` this is rejected with
`error: expression is not assignable`, matching C semantics where the ternary
result is a prvalue that cannot be assigned to. In DXC with `-HV 202x` the same
source compiles successfully, matching C++ semantics where the ternary result is
a glvalue referring to either `X` or `Y`. HLSL needs to pick a single,
well-defined behavior.

## Proposed solution

HLSL adopts the C++ value category rules for the conditional (ternary)
operator. When the second and third operands are both glvalues of the same type,
the result of the ternary is a glvalue of that type and may be used as the
operand of an assignment. Otherwise, the result is a prvalue.

To avoid silently changing the behavior of existing shaders, this change is
scoped by language version:

* **HLSL 2021** retains its existing behavior, implemented by the custom
  `SemaHLSL` ternary validation code.
* **HLSL 202x** uses the new behavior by following the C++ value category rules
  for the ternary operator, rather than falling back to the unspecified mixed
  behavior present today.

This also fixes the two DXC bugs described in the motivation: the result value
category will correctly reflect the operands, so a glvalue result will no longer
be mistyped as an rvalue, and an rvalue result will correctly reject assignment.