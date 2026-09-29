---
title: 0016 - Non-member Operator Overloading
slug: "0016"
params:
  authors:
  - llvm-beanz: Chris Bieneman
  sponsors:
  - llvm-beanz: Chris Bieneman
  status: Accepted
---

## Implementation Status

|   | DXC     | Clang    |
|---|---------|----------|
| `const` member functions | [Complete](https://github.com/microsoft/DirectXShaderCompiler/issues/8964) | Complete |

## Introduction

HLSL 2021 introduced operator overloading for member operators of user defined
data types. Only supporting member operators has some drawbacks, specifically
defining binary operators where the LHS is a built-in type is impossible,
additionally scoping operators to namespaces is also impossible.

## Motivation

Beyond common use cases where global operators are nice to have, users adopting
HLSL 2021 have provided feedback that global operator overloading would be a
significant benefit.

HLSL 2021's introduction of short circuiting boolean operators users have been
forced to translate their code that operates on HLSL vector types to use the
new `select`, `and` and `or` intrinsics. We believe the new intrinsics are the
right step for the language in removing ambiguity and clearly expressing code
meaning. Global operator overloading provides an opportunity for the language to
remain clear and unambiguous, while allowing users to define custom operators
that allow them to not migrate legacy code.

## Proposed solution

This change requires fully adopting C++ rules for operator overload resolution
and supporting defining global and namespace scoped operator overloads. The
limitations currently in place on operator overloading (disallowing overloading
operators that idiomatically return references) will remain in effect on
non-member operators as well unless the restrictions are lifted as proposed in
[0006 Reference Types](0006-reference types.md).

Because this solution should not break existing code, it could also be enabled
under HLSL 2021 as an extension. Using the feature in HLSL 2021 mode as an
extension will produce warnings so that users can be aware of portability issues
that may arise between compiler versions.

## Alternatives considered

Non-member operator overloading is a feature that is generally useful, an no
alternatives have been considered to the feature itself. Reflecting on the
problems caused by HLSL 2021 removing boolean operators from vector types other
options were considered.

One considered option was to roll back the HLSL 2021 removal of vector boolean
operators. Operator short circuiting was introduced in HLSL 2021 to reduce
behavioral differences between HLSL and C/C++. With operator short circuiting,
vector operators aren't intuitive because they can't short circuit.

Having scalar operators short circuit and vector operators not was also
considered. The argument against that approach is that having two code
representations that look the same but behave differently is unintuitive. This
gets more unintuitive when you consider that, with the introduction of templates,
the same literal line of code could be used for both vector and scalar
conditionals with different behavior.

For these reasons, this proposal posits that HLSL 2021's decision is the correct
approach for the language. This proposal gives users the ability to introduce
source compatibility if they choose, but at their own maintenance expense. It
also adopts behavior that is consistent with C++ for evaluation of logical
operators.

## Detailed Design

#### Overloaded Operators `[Overload.Operators]`

```
operator-function-id:
  `operator` operator
operator: one of
  `+` `-` `*` `/` `%` `^` `&` `|` `~` `!` `<` `>` `<<` `>>` `<=` `>=` `&&` `||` `,` `()` `[]`
```

The operators `+`, `-`, `*`, and `&` may only be overloaded in their binary
form.

The `.`, `::` and `?:` operators cannot be overloaded.

Operator functions may be called directly by their name in the form `operator@`
or through the resolution of an overload from an operator expression.

An overloaded operator function must be either a non-static member function or a
non-member function, and must have at least one parameter whose type is a class
or enumeration.

An overloaded operator may not change the number of operands of an operator,
except the function call operator which may have any number of operands.

The meaning of the `,` operator, which is pre-defined for all types, can be
changed by operator overloading.

Overloaded operator functions are inherited from base classes in the same way as
other base class member functions.

Only an overloaded call operator may have default arguments, no other operator
functions may be defined with default arguments. All operator functions must
take exactly the number of parameters of the corresponding operator as defined
in this subclause.

##### Unary Operators

An overloaded prefix unary operator must be implemented by a non-static member
function with no parameters or a non-member function with one parameter.

Postfix unary operators are not overloadable.

##### Binary Operators

An overloaded binary operator must be implemented by a non-static member
function with one parameter or a non-member function with two parameters.

##### Function Call Operator

An overloaded function call operator must be a non-static member function with
an arbitrary number of parameters, and may have default arguments. Function call
operator functions are overload candidates for the function call syntax when the
_postfix-expression_ is an object of class type.

##### Subscript operator

An overloaded subscript operator must be a non-static member function with one
parameter. Subscript operator functions are overload candidates for the
subscript syntax when the _postfix-expression_ is an object of class type.

#### Built-in Operators `[Overload.Builtin]`

For binary operators on arithmetic types, the result type is called the
_promoted expression type_ as determined by usual arithmetic conversions
(\ref{Expr.Conv}).

For all types `T` where `T` is an arithmetic type (\ref{Basic.Types.Arithmetic});
operators will be defined of the forms:

```
T operator+(T );
T operator-(T );
T operator~(T );
```

For all types `L`, `R` and `LR`, where `L` and `R` are any arithmetic type
(\ref{Basic.Types.Arithmetic}), and `LR` is the promoted expression type;
operators will be defined of the forms:

```
LR operator*(L , R );
LR operator/(L , R );
LR operator+(L , R );
LR operator-(L , R );
bool operator<(L , R );
bool operator>(L , R );
bool operator<=(L , R );
bool operator>=(L , R );
bool operator==(L , R );
bool operator!=(L , R );
LR operator%(L , R );
```

For all types `T` where `T` is an enumeration type (\ref{Decl.Enum}); operators
will be defined of the form:

```
bool operator<(T , T );
bool operator>(T , T );
bool operator<=(T , T );
bool operator>=(T , T );
bool operator==(T , T );
bool operator!=(T , T );
```

For all types `T` where `T` is an integral type
(\ref{Basic.Types.Arithmetic}); operators will be defined of the form:

```
LR operator&(L , R );
LR operator^(L , R );
LR operator|(L , R );
L operator<<(L , R );
L operator>>(L , R );
```

For all types `L` and `R` where `L` and `R` are arithmetic types
(\ref{Basic.Types.Arithmetic}), and `CVQ` is a _cv-qualifier_; operators will be
defined of the form:

```
CVQ L & operator=(CVQ L &, R );
CVQ L & operator*=(CVQ L &, R );
CVQ L & operator/=(CVQ L &, R );
CVQ L & operator+=(CVQ L &, R );
CVQ L & operator-=(CVQ L &, R );
CVQ L & operator%=(CVQ L &, R );
```

For all types `L` and `R` where `L` and `R` are integral types
(\ref{Basic.Types.Arithmetic}), and `CVQ` is a _cv-qualifier_; operators will be
defined of the form:
```
CVQ L & operator<<=(CVQ L &, R );
CVQ L & operator>>=(CVQ L &, R );
CVQ L & operator&=(CVQ L &, R );
CVQ L & operator^=(CVQ L &, R );
CVQ L & operator|=(CVQ L &, R );
```

For the boolean type `bool` operators will be defined of the form:

```
bool operator!(bool);
bool operator&&(bool, bool);
bool operator||(bool, bool);
```

For all types `L`, `R` and `LR`, where `L` and `R` are any arithmetic type
(\ref{Basic.Types.Arithmetic}), and `LR` is the promoted expression type;
the ternary operator will be defined of the form:

```
LR operator?:(bool, L , R );
```

For all types `T`, a ternary operator will be defined of the form:

```
T operator?:(bool, T , T );
```

## Acknowledgments

This proposal is the result of conversations with users and teammates. Thank you
everyone who contributed feedback on HLSL 2021.
