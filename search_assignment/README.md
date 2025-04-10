# Description
Given the data of actors and  the movies they are participated in. Let's find the shortest path from one actor to another by using breadth-first search.

For example, one can prompt in:

```
Name: tom hanks
Name: noomi rapace
```

Then the program will give results like:

```
2 degrees of separation.
1: Tom Hanks and John Malkovich starred in The Great Buck Howard
2: John Malkovich and Noomi Rapace starred in Unlocked
```

Or 


```
Name: chris sarandon
Name: peter haber
```

This will take a much longer time to search, but in the end it will tell:

```
4 degrees of separation.
1: Chris Sarandon and Joanna Gleason starred in Road Ends
2: Joanna Gleason and Bryan Brown starred in F/X2
3: Bryan Brown and Lena Endre starred in Limbo
4: Lena Endre and Peter Haber starred in Juloratoriet
```

# Learning point 

This is the first week's project in the CS50 for AI. All codes are prefilled except for the function `shortest_path(source, target)`. By working on the `shortest_path(source, target)`, I learned deeper about `class` in Python and BFS algorithm.

