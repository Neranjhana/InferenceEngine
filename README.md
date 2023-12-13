# InferenceEngine
Built an inference engine which determines whether or not a new query can be inferred from an existing knowledge base

Used backward chaining to solve this

Problem:
We are given a knowledge base and a query sentence, and we need to determine if the query can be inferred from the information given in the knowledge base. 

Input:
You will be given the knowledge base and the query in a text file called input.txt.
The first line of the input file contains the query. The second line contains an integer n specifying
the number of clauses in the knowledge base. The remaining lines contain the clauses in the
knowledge base, one per line. Each clause is written in one of the following forms:
1) as an implication of the form p1 ∧ p2 ∧ ... ∧ pn ⇒ q, whose premise is a conjunction of
atomic sentences and whose conclusion is a single atomic sentence.
2) as a fact with a single atomic sentence: q
Each atomic sentence is a predicate applied to a certain number of arguments. 

Output:
If the query sentence can be inferred from the knowledge base, your output should be TRUE, otherwise, FALSE. The answers are stored in output.txt file which the code generates
