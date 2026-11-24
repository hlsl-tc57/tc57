---
title: "NNNN - 0/1 Swizzles"
slug: "NNNN"
draft: true
params:
  authors:
    - pow2clk: Gregory Roth
  sponsors:
    - pow2clk: Gregory Roth
  status: Under Consideration
---


## Introduction

Adds the ability to specify explicit 0 or 1 constant values alongside existing
indexing swizzle components rgba and xyzw. This inserts the values in the
appropriate element type and representation into the output vector at the
locations corresponding to the position in the swizzle.

## Motivation

* [microsoft/hlsl-specs#70](https://github.com/microsoft/hlsl-specs/issues/70)
* [webgpu/webgpu#732](https://github.com/gpuweb/gpuweb/issues/732) (Not HLSL,
but the same motivation applies)

The current way to add constant values to the end of an existing vector to form
a longer vector is a bit verbose e.g. `float4(vec3, 1.0)`. To insert an element
into another part of the vector is even worse e.g. `float3(vec3.x, 0.0, vec3.z)`.

What's more, the first method will be disallowed with the introduction of
[0011 Strict Initializer Lists](0011-strict-initializer-lists.md). This will
leave users with a very cumbersome replacement:
`float4(vec3.x, vec3.y, vec3.z, 1.0)`

## Proposed solution

Simply allowing 0 and 1 to represent those values in a swizzle sequence will
both simplify existing code and provide a way to prepare for or react to a
breaking change to come with minimal effort and elegant syntax.

The complication involves scalar literals where a swizzle sequence that begins
with a number or only consists of a number is ambiguous with a float literal at
least at first. To avoid this problem, vector literals formed by literal scalars
followed by dot operator and swizzle sequence won't be allowed to have 0 or 1 as
the first element.

## Detailed design

<!-- I know it said not to include this yet, but I wrote it up before I started
this, so I figured I may as well include it -->

### Addition to [Lex.Literal.Vector]

> 0 and 1 scalar elements are added to the scalar-element-sequence grammar

```diff
 \begin{grammar}
   \define{vector-literal}\br
   integer-literal \texttt{.} scalar-element-sequence\br
   floating-literal \texttt{.} scalar-element-sequence
 
   \define{scalar-element-sequence}\br
-  scalar-element-sequence-x\br
-  scalar-element-sequence-r
+  \texttt{x} \opt(scalar-element-sequence-x)\br
+  \texttt{r} \opt(scalar-element-sequence-r)\br
 
   \define{scalar-element-sequence-x}\br
-  \texttt{x}\br
-  scalar-element-sequence-x \texttt{x}
+  scalar-element-x01\br
+  scalar-element-sequence-x scalar-element-r01\br
 
   \define{scalar-element-sequence-r}\br
-  \texttt{r}\br
-  scalar-element-sequence-r \texttt{r}
+  scalar-element-r01\br
+  scalar-element-sequence-r scalar-element-r01\br
+
+  \define{scalar-element-x01} \textnormal{one of}\br
+  \terminal{x 0 1}\br
+
+  \define{scalar-element-r01} \textnormal{one of}\br
+  \terminal{r 0 1}\br
+
 \end{grammar}
```

> The description of the `scalar-element-sequence` is expanded to describe the
new behavior:

A _scalar-element-sequence_ is an `r` followed by an optional
_vector-swizzle-sequence-r_ or a `x` followed by an optional
_vector-swizzle-sequence-x_. Each sequence is some combination of `0`, `1`, and
either `r` or `x` components. Each `r` or `x` component refers to the value of
the scalar literal. Explicit vector swizzle components `0` or `1` correspond to
constant values inserted into the corresponding element of the output vector of
the same element type and corresponding representation of the postfix expression
for the values of zero and one for `0` and `1` respectively.

A _scalar-element-sequence_ with no explicit components is equivalent to a
vector splat conversion performed on the _integer-literal_ or _floating-literal_
value [Conv.vsplat].

### Addition to [Expr.Post.Swizzle]

> Description of when a postfix expression might be considered an lvalue is
expanded

If the postfix expression before the dot is an lvalue, is not a scalar, and the
_swizzle-component-sequence_ contains no repeated nor explicit components (`0`
or `1`), the swizzle expression is an lvalue; otherwise it is a prvalue.

> 0 and 1 scalar elements are added to the  grammar

```diff
 \begin{grammar}
   \define{vector-swizzle-component-sequence}\br
   swizzle-component-sequence-rgba\br
   swizzle-component-sequence-xyzw\br

   \define{swizzle-component-sequence-rgba}\br
   swizzle-component-rgba\br
+  swizzle-component-explicit\br
   swizzle-component-sequence-rgba swizzle-component-rgba\br
+  swizzle-component-sequence-rgba swizzle-component-explicit\br
 
   \define{swizzle-component-sequence-xyzw}\br
   swizzle-component-xyzw\br
+  swizzle-component-explicit\br
   swizzle-component-sequence-xyzw swizzle-component-xyzw\br
+  swizzle-component-sequence-xyzw swizzle-component-explicit\br
+
+  \define{swizzle-component-explicit} \textnormal{one of}\br
+  \terminal{0 1}\br

   \define{swizzle-component-rgba} \textnormal{one of}\br
   \terminal{r g b a}\br

   \define{swizzle-component-xyzw} \textnormal{one of}\br
   \terminal{x y z w}
 \end{grammar}
```

> The description of _vector-swizzle-component-sequence_ is expanded to describe the
new behavior:

A _vector-swizzle-component-sequence_ consists of one or more _indexing vector
swizzle components_, the _swizzle-component-rgba_ or _swizzle-component-xyzw_
forms, and the _explicit swizzle components_, the _swizzle-component-explicit_
form. The two indexing forms may not be mixed in the same
_vector-swizzle-component-sequence_. The type of a swizzle expression is a
vector of the same element type as the vector postfix expression or type of the
scalar postfix expression before the dot, with a number of elements equal to the
number of components in the _vector-swizzle-component-sequence_.

_Indexing vector swizzle components_ map to elements of the vector in the
following way:

> At the end of the subsection, add a description of how the explicit swizzles
affect the output vector

Explicit vector swizzle components correspond to constant values inserted into
the corresponding element of the output vector of the same element type and
corresponding representation of the postfix expression for the values of zero
and one for `0` and `1` respectively.

## Alternatives considered

Rather than single out vector literals with a different syntax, we might have
disallowed 0 or 1 in the first swizzle position outright. This was rejected
because vector literals already have their own grammar and limitations and there
are some use cases such as quaternions that would benefit from the ability to
insert a constant value at the front of a vector.

The literal vector case may be ultimately left out of this entirely instead of
limited to starting with an `x` or an `r`. It would simplify the spec some.
It is of uncertain utility. It does enable something that is easy to do and
creates maximum consistency between the left sides of the two swizzle targets
which might minimize user astonishment.